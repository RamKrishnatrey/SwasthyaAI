import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetManifest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str
    task: str
    schema_version: str = Field(alias="schema")
    labels: list[str] = Field(min_length=1)
    languages: list[str] = Field(min_length=1)
    license: str
    provenance: str
    path: str

    def public_status(self) -> dict[str, Any]:
        return self.model_dump(exclude={"path", "schema_version"}, by_alias=True) | {"schema": self.schema_version}


def load_dataset_manifests(directory: Path) -> list[DatasetManifest]:
    manifests = []
    for path in sorted(directory.glob("*.json")):
        try:
            manifests.append(DatasetManifest.model_validate_json(path.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            continue
    return manifests


def compatible_datasets(items: list[DatasetManifest], task: str) -> list[list[DatasetManifest]]:
    groups: dict[tuple, list[DatasetManifest]] = {}
    for item in items:
        if item.task != task:
            continue
        key = (item.schema_version, tuple(sorted(item.labels)), tuple(sorted(item.languages)), item.license, item.provenance)
        groups.setdefault(key, []).append(item)
    return list(groups.values())
