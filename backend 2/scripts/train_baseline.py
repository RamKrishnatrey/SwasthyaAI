"""Train/evaluate a baseline text classifier on an explicitly labeled CSV.

This generic research utility is NOT a clinical model and must not be used for care decisions.
Example: python scripts/train_baseline.py data/labeled.csv --text-column text --label-column label
The script refuses to run without explicit text and label columns.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--text-column", required=True)
    parser.add_argument("--label-column", required=True)
    parser.add_argument("--output-dir", default="artifacts/research_baseline")
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()
    if not 0.1 <= args.test_size <= 0.4:
        raise SystemExit("--test-size must be between 0.1 and 0.4")
    try:
        import pandas as pd
        import joblib
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
    except ImportError:
        raise SystemExit("Install optional ML tools: python -m pip install pandas scikit-learn joblib")
    path = Path(args.csv_path)
    df = pd.read_csv(path)
    if args.text_column not in df or args.label_column not in df:
        raise SystemExit(f"Columns not found. Available columns: {list(df.columns)}")
    data = df[[args.text_column, args.label_column]].dropna()
    data[args.text_column] = data[args.text_column].astype(str).str.strip()
    data = data[data[args.text_column] != ""]
    counts = data[args.label_column].value_counts()
    if len(data) < 30 or len(counts) < 2 or counts.min() < 2:
        raise SystemExit("Need at least 30 labeled rows, 2 classes, and at least 2 rows per class.")
    stratify = data[args.label_column] if counts.min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        data[args.text_column], data[args.label_column], test_size=args.test_size,
        random_state=42, stratify=stratify,
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=50000)),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    report = {
        "dataset": str(path), "text_column": args.text_column, "label_column": args.label_column,
        "rows_used": int(len(data)), "train_rows": int(len(x_train)), "test_rows": int(len(x_test)),
        "accuracy": float(accuracy_score(y_test, predicted)),
        "classification_report": classification_report(y_test, predicted, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predicted, labels=model.classes_).tolist(),
        "labels": [str(label) for label in model.classes_],
        "limitations": "Research baseline only; dataset quality, leakage, subgroup performance, external validation, calibration, clinical review, and safety testing are not established. Do not use for diagnosis or triage.",
    }
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "baseline.joblib")
    (out / "evaluation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("rows_used", "train_rows", "test_rows", "accuracy", "labels", "limitations")}, indent=2))
    print(f"Saved research model and metrics under {out.resolve()}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
