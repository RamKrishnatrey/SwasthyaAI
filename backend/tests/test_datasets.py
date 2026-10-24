import json

from backend.swasthyaai.datasets import DatasetManifest, compatible_datasets, load_dataset_manifests


def manifest(**changes):
    values = {
        "name": "triage-a",
        "task": "care_triage",
        "schema": "triage-v1",
        "labels": ["care_type", "urgency"],
        "languages": ["English", "Hindi"],
        "license": "MIT",
        "provenance": "synthetic hackathon dataset",
        "path": "private/location/triage.jsonl",
    }
    values.update(changes)
    return DatasetManifest(**values)


def test_only_manifests_with_compatible_task_schema_language_and_license_are_grouped():
    first = manifest(name="first")
    compatible = manifest(name="second")
    different_schema = manifest(name="third", schema="diagnosis-v1")
    different_language = manifest(name="fourth", languages=["English"])
    different_license = manifest(name="fifth", license="unknown")
    different_task = manifest(name="sixth", task="image_analysis")

    groups = compatible_datasets(
        [first, compatible, different_schema, different_language, different_license, different_task],
        "care_triage",
    )

    assert [[item.name for item in group] for group in groups] == [
        ["first", "second"],
        ["third"],
        ["fourth"],
        ["fifth"],
    ]


def test_manifest_loader_reads_json_and_rejects_incomplete_metadata(tmp_path):
    (tmp_path / "valid.json").write_text(
        json.dumps({
            "name": "triage",
            "task": "care_triage",
            "schema": "triage-v1",
            "labels": ["care_type", "urgency"],
            "languages": ["English"],
            "license": "MIT",
            "provenance": "synthetic",
            "path": "data/triage.jsonl",
        }),
        encoding="utf-8",
    )
    (tmp_path / "incomplete.json").write_text('{"name":"missing metadata"}', encoding="utf-8")

    manifests = load_dataset_manifests(tmp_path)

    assert [item.name for item in manifests] == ["triage"]


def test_manifest_public_metadata_never_exposes_raw_path():
    item = manifest()

    assert "private/location/triage.jsonl" not in str(item.public_status())
