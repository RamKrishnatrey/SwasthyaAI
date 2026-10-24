"""Train and evaluate a CPU-friendly text baseline on local Parquet splits.

Expected files (download separately and do not commit the dataset):
  data/english_symptoms/data/train-00000-of-00001.parquet
  data/english_symptoms/data/validation-00000-of-00001.parquet
  data/english_symptoms/data/test-00000-of-00001.parquet

This is an experimental dataset classifier, not a diagnostic or triage device.
"""
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "english_symptoms" / "data"
OUT = ROOT / "models"
OUT.mkdir(parents=True, exist_ok=True)

def load_split(name: str) -> pd.DataFrame:
    path = DATA / f"{name}-00000-of-00001.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Obtain the dataset under its licence before training."
        )
    df = pd.read_parquet(path).dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(int)
    return df[df["text"] != ""]

train = load_split("train")
validation = load_split("validation")
test = load_split("test")

def features() -> FeatureUnion:
    return FeatureUnion([
        ("word", TfidfVectorizer(
            ngram_range=(1, 2), max_features=50000,
            sublinear_tf=True, strip_accents="unicode"
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb", ngram_range=(3, 5),
            max_features=50000, sublinear_tf=True
        )),
    ])

candidates = {
    "svm_word_char": Pipeline([
        ("features", features()),
        ("classifier", LinearSVC(C=1.0)),
    ]),
    "logistic_word_char": Pipeline([
        ("features", features()),
        ("classifier", LogisticRegression(max_iter=3000, C=2.0)),
    ]),
}

rows = []
fitted = {}
print(f"Rows: train={len(train)}, validation={len(validation)}, test={len(test)}")
print(f"Numeric labels: {sorted(train['label'].unique().tolist())}")

for name, model in candidates.items():
    print(f"\nTraining {name}...")
    model.fit(train["text"], train["label"])
    pred = model.predict(validation["text"])
    row = {
        "model": name,
        "validation_accuracy": float(accuracy_score(validation["label"], pred)),
        "validation_macro_f1": float(f1_score(validation["label"], pred, average="macro")),
    }
    rows.append(row)
    fitted[name] = model
    print(f"Validation accuracy: {row['validation_accuracy']:.2%}")
    print(f"Validation macro-F1: {row['validation_macro_f1']:.4f}")

comparison = pd.DataFrame(rows).sort_values("validation_macro_f1", ascending=False)
comparison.to_csv(OUT / "official_validation_comparison.csv", index=False)
best_name = str(comparison.iloc[0]["model"])
best = fitted[best_name]

test_pred = best.predict(test["text"])
test_accuracy = float(accuracy_score(test["label"], test_pred))
test_f1 = float(f1_score(test["label"], test_pred, average="macro"))
report = classification_report(test["label"], test_pred, output_dict=True, zero_division=0)

joblib.dump(best, OUT / "best_official_split_model.joblib")
pd.DataFrame({
    "text": test["text"],
    "actual_label_id": test["label"],
    "predicted_label_id": test_pred,
}).to_csv(OUT / "official_test_predictions.csv", index=False)

metrics = {
    "selected_model": best_name,
    "train_examples": int(len(train)),
    "validation_examples": int(len(validation)),
    "test_examples": int(len(test)),
    "test_accuracy": test_accuracy,
    "test_macro_f1": test_f1,
    "classification_report_numeric_labels": report,
    "label_mapping": None,
    "note": (
        "Label IDs are left numeric until the dataset's authoritative mapping is verified. "
        "Synthetic/balanced dataset metrics do not establish clinical validity."
    ),
}
(OUT / "official_test_metrics.json").write_text(
    json.dumps(metrics, indent=2), encoding="utf-8"
)

print(f"\nSelected by validation macro-F1: {best_name}")
print(f"Final held-out test accuracy: {test_accuracy:.2%}")
print(f"Final held-out test macro-F1: {test_f1:.4f}")
print(classification_report(test["label"], test_pred, zero_division=0))
print(f"Saved model: {OUT / 'best_official_split_model.joblib'}")
print(f"Saved metrics: {OUT / 'official_test_metrics.json'}")
print("Reminder: verify numeric label mapping and evaluate for dataset leakage.")
