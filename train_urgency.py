import json
from pathlib import Path

import joblib
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)

print("Loading dataset...")
ds = load_dataset("Tulsiandhare/Multilingual_medical_symptom_triage", split="train")
df = ds.to_pandas()[["patient_query", "urgency"]].dropna()
df["patient_query"] = df["patient_query"].astype(str).str.strip()
df["urgency"] = df["urgency"].astype(str).str.strip()
df = df[(df["patient_query"] != "") & (df["urgency"] != "")]
df = df.drop_duplicates(subset=["patient_query", "urgency"])

print(f"Usable rows: {len(df)}")
print("\nUrgency label counts:")
print(df["urgency"].value_counts().to_string())

X_train, X_test, y_train, y_test = train_test_split(
    df["patient_query"],
    df["urgency"],
    test_size=0.2,
    random_state=42,
    stratify=df["urgency"],
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100000,
        sublinear_tf=True,
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
    )),
])

print("\nTraining baseline model...")
model.fit(X_train, y_train)
predictions = model.predict(X_test)

report = classification_report(
    y_test, predictions, output_dict=True, zero_division=0
)
metrics = {
    "dataset": "Tulsiandhare/Multilingual_medical_symptom_triage",
    "target": "urgency",
    "input_feature": "patient_query",
    "training_rows": len(X_train),
    "test_rows": len(X_test),
    "accuracy": accuracy_score(y_test, predictions),
    "classification_report": report,
    "confusion_matrix": confusion_matrix(
        y_test, predictions, labels=model.classes_
    ).tolist(),
    "class_order": model.classes_.tolist(),
    "limitations": [
        "Synthetic, rule-based dataset labels; not clinically validated",
        "Prototype only; not safe for real-world triage",
        "Test performance does not establish clinical safety",
    ],
}

joblib.dump(model, OUT / "urgency_baseline.joblib")
(OUT / "urgency_metrics.json").write_text(
    json.dumps(metrics, indent=2), encoding="utf-8"
)

print("\nAccuracy:", round(metrics["accuracy"], 4))
print("\nEvaluation report:")
print(classification_report(y_test, predictions, zero_division=0))
print("Confusion matrix (class order:", list(model.classes_), ")")
print(confusion_matrix(y_test, predictions, labels=model.classes_))
print("\nSaved model: artifacts/urgency_baseline.joblib")
print("Saved metrics: artifacts/urgency_metrics.json")
print("\nTraining complete.")
