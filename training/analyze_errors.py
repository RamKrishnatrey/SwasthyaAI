"""Analyze errors for the random-split baseline in models/best_text_model.joblib."""
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "english_symptoms" / "dataset_v2-final_english.csv")
df = df.dropna(subset=["text", "label"]).drop_duplicates(subset=["text", "label"])
df["text"] = df["text"].astype(str)
df["label"] = df["label"].astype(str)
_, X_test, _, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)
model = joblib.load(ROOT / "models" / "best_text_model.joblib")
pred = model.predict(X_test)
wrong = pd.DataFrame({"text": X_test.reset_index(drop=True), "actual": y_test.reset_index(drop=True), "predicted": pred})
wrong = wrong[wrong.actual != wrong.predicted]
print("Accuracy:", f"{accuracy_score(y_test, pred):.2%}")
print("Errors:", len(wrong))
for _, row in wrong.head(15).iterrows():
    print("\nACTUAL:", row.actual, "\nPREDICTED:", row.predicted, "\nTEXT:", row.text[:400])
wrong.to_csv(ROOT / "models" / "error_analysis.csv", index=False)
print("Saved models/error_analysis.csv")
