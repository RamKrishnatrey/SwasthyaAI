"""Profile downloaded dataset files before any training.

Usage: python scripts/evaluate_dataset.py data/raw/intelmedica__nursing-sentences-1
Writes a JSON report. This is a data-quality profile, not clinical model evaluation.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SUPPORTED = {".csv", ".tsv", ".json", ".jsonl", ".parquet"}

def load_frame(path: Path):
    import pandas as pd
    if path.suffix == ".parquet": return pd.read_parquet(path)
    if path.suffix == ".tsv": return pd.read_csv(path, sep="\t")
    if path.suffix == ".csv": return pd.read_csv(path)
    if path.suffix == ".jsonl": return pd.read_json(path, lines=True)
    return pd.read_json(path)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Dataset file or folder")
    parser.add_argument("--output", default="dataset_profile.json")
    args = parser.parse_args()
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("Install data tools: python -m pip install pandas pyarrow")
    root = Path(args.path)
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    report = {"path": str(root), "files": [], "note": "Data-quality profile only; not model accuracy, safety, or clinical validation."}
    for path in files:
        try:
            df = load_frame(path)
            entry = {"file": str(path), "rows": int(len(df)), "columns": {str(col): {"dtype": str(df[col].dtype), "missing": int(df[col].isna().sum()), "unique": int(df[col].nunique(dropna=True))} for col in df.columns}}
            for col in df.select_dtypes(include=["object", "string"]).columns:
                if df[col].nunique(dropna=True) <= 30:
                    entry["columns"][str(col)]["top_values"] = {str(k): int(v) for k, v in df[col].value_counts(dropna=True).head(10).items()}
            report["files"].append(entry)
        except Exception as exc:
            report["files"].append({"file": str(path), "error": str(exc)})
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.output}; profiled {len(report['files'])} file(s). Review errors, licensing, and schema before use.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
