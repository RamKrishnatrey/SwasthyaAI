import json
from pathlib import Path

import joblib
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)

print("Loading dataset...")
df = load_dataset(
    "Tulsiandhare/Multilingual_medical_symptom_triage",
    split="train"
).to_pandas()

df["patient_query"] = df["patient_query"].fillna("").astype(str).str.strip()
df["urgency"] = df["urgency"].fillna("").astype(str).str.strip()
df = df[(df["patient_query"] != "") & (df["urgency"] != "")]

# Exclude texts with conflicting labels and retain one row per query.
counts = df.groupby("patient_query")["urgency"].nunique()
ambiguous = set(counts[counts > 1].index)
df = df[~df["patient_query"].isin(ambiguous)]
df = df.drop_duplicates(subset=["patient_query"])

print("Clean rows:", len(df))
print("Excluded ambiguous query texts:", len(ambiguous))
print("Classes:", df["urgency"].value_counts().to_dict())

X_train, X_test, y_train, y_test = train_test_split(
    df["patient_query"],
    df["urgency"],
    test_size=0.2,
    random_state=42,
    stratify=df["urgency"],
)

features = FeatureUnion([
    ("word", TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        max_features=100000,
        sublinear_tf=True,
    )),
    ("char", TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        min_df=2,
        max_features=150000,
        sublinear_tf=True,
    )),
])

model = Pipeline([
    ("features", features),
    ("classifier", LinearSVC(class_weight="balanced")),
])

print("\nTraining word + character TF-IDF / Linear SVM...")
model.fit(X_train, y_train)
pred = model.predict(X_test)

report = classification_report(
    y_test, pred, output_dict=True, zero_division=0
)
metrics = {
    "model": "word_char_tfidf_linear_svc",
    "target": "urgency",
    "input": "patient_query",
    "rows_after_cleaning": len(df),
    "train_rows": len(X_train),
    "test_rows": len(X_test),
    "accuracy": float(accuracy_score(y_test, pred)),
    "macro_f1": float(f1_score(y_test, pred, average="macro")),
    "classification_report": report,
    "confusion_matrix": confusion_matrix(
        y_test, pred, labels=model.classes_
    ).tolist(),
    "class_order": model.classes_.tolist(),
    "limitations": [
        "Dataset labels are not clinically validated",
        "Synthetic dataset performance does not establish real-world safety",
        "This is an experimental baseline, not a clinical triage system",
    ],
}

joblib.dump(model, OUT / "urgency_svm_v2.joblib")
(OUT / "urgency_svm_v2_metrics.json").write_text(
    json.dumps(metrics, indent=2), encoding="utf-8"
)

print("\nAccuracy:", round(metrics["accuracy"], 4))
print("Macro-F1:", round(metrics["macro_f1"], 4))
print("\nClass report:")
print(classification_report(y_test, pred, zero_division=0))
print("\nConfusion matrix (", list(model.classes_), "):")
print(confusion_matrix(y_test, pred, labels=model.classes_))
print("\nSaved artifacts/urgency_svm_v2.joblib")
print("Saved artifacts/urgency_svm_v2_metrics.json")
