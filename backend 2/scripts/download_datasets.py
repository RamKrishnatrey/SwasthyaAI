"""Download selected Hugging Face datasets for review; this does not train a model.

Run from backend 2:
  python scripts/download_datasets.py --dataset intelmedica/nursing-sentences-1
  python scripts/download_datasets.py --dataset intelmedica/medical-tts-parquet-1

Review each repository's current license, terms, and README before using files.
Gated repositories require normal Hugging Face access; this script does not bypass it.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ALLOWED_DATASETS = {
    "intelmedica/nursing-sentences-1",
    "intelmedica/medical-tts-parquet-1",
    "jfmdai/physician-sentences",
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", action="append", choices=sorted(ALLOWED_DATASETS), required=True)
    parser.add_argument("--output", default="data/raw")
    args = parser.parse_args()
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError:
        raise SystemExit("Install the optional tool first: python -m pip install huggingface_hub")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    for dataset_id in args.dataset:
        target = output / dataset_id.replace("/", "__")
        print(f"Inspecting {dataset_id} ...")
        try:
            info = api.dataset_info(dataset_id)
            files = api.list_repo_files(dataset_id, repo_type="dataset")
        except Exception as exc:
            print(f"Could not access {dataset_id}: {exc}")
            print("If gated, sign in with hf auth login and accept repository terms on Hugging Face.")
            continue
        card = getattr(info, "cardData", None) or {}
        metadata = {
            "dataset_id": dataset_id,
            "sha": getattr(info, "sha", None),
            "license": card.get("license"),
            "tags": card.get("tags", []),
            "files": files,
            "note": "Review the current dataset card/license before use. Not clinically validated.",
        }
        (target.parent / f"{target.name}.metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Repository files: {len(files)}; declared license: {metadata['license'] or 'not declared in card metadata'}")
        print("Review the dataset card and license before research or redistribution.")
        try:
            snapshot_download(repo_id=dataset_id, repo_type="dataset", local_dir=str(target), allow_patterns=["README.md", "*.parquet", "*.csv", "*.json", "*.jsonl", "*.tsv", "*.wav", "*.mp3", "*.flac"])
            print(f"Downloaded supported file types to: {target}")
        except Exception as exc:
            print(f"Download failed for {dataset_id}: {exc}")
    print("Download pass finished. No training or evaluation was run.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
