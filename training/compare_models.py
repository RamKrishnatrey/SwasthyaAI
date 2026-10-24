"""Compare TF-IDF classifiers on a random holdout for exploratory use.

For final reporting, prefer train_official_splits.py and its validation/test split.
This script writes its chosen model and error-analysis artifacts into models/.
"""
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import accuracy_score, f1_score, classification_report

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "english_symptoms" / "dataset_v2-final_english.csv"
out = ROOT / "models"
out.mkdir(exist_ok=True)
df = pd.read_csv(source).dropna(subset=["text", "label"]).copy()
df["text"] = df["text"].astype(str).str.strip()
df["label"] = df["label"].astype(str).str.strip()
df = df[(df.text != "") & (df.label != "")].drop_duplicates(subset=["text", "label"])
X_train, X_test, y_train, y_test = train_test_split(
    df.text, df.label, test_size=0.2, random_state=42, stratify=df.label
)

def features():
    return FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=50000, sublinear_tf=True)),
    ])

models = {
    "logistic_word_char": Pipeline([("features", features()), ("clf", LogisticRegression(max_iter=3000, C=2))]),
    "svm_word_char": Pipeline([("features", features()), ("clf", LinearSVC(C=1.0))]),
    "svm_word": Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=50000)), ("clf", LinearSVC(C=1.0))]),
    "complement_nb": Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=30000)), ("clf", ComplementNB(alpha=0.1))]),
}
rows, fitted = [], {}
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    rows.append({"model": name, "accuracy": accuracy_score(y_test, pred), "macro_f1": f1_score(y_test, pred, average="macro")})
    fitted[name] = model
comparison = pd.DataFrame(rows).sort_values("macro_f1", ascending=False)
comparison.to_csv(out / "model_comparison.csv", index=False)
best_name = str(comparison.iloc[0]["model"])
joblib.dump(fitted[best_name], out / "best_text_model.joblib")
print(comparison.to_string(index=False))
print("Best model:", best_name)
print(classification_report(y_test, fitted[best_name].predict(X_test), zero_division=0))
