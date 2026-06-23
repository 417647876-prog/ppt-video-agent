from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SlideContent:
    index: int
    title: str
    body: str
    raw_text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SlideScript:
    slide_index: int
    title: str
    script: str
    target_chars: int
    style: str

    def to_dict(self) -> dict:
        return asdict(self)
