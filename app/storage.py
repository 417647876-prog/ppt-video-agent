from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Sequence


def _to_plain_object(item: Any) -> Any:
    if is_dataclass(item):
        return asdict(item)
    if hasattr(item, "to_dict"):
        return item.to_dict()
    return item


def to_json_bytes(items: Sequence[Any]) -> bytes:
    plain_items = [_to_plain_object(item) for item in items]
    text = json.dumps(plain_items, ensure_ascii=False, indent=2)
    return text.encode("utf-8")


def save_json(path: Path, items: Sequence[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_json_bytes(items))
