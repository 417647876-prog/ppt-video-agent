from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SlideContent:
    index: int
    title: str
    body: str
    raw_text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SlideScript:
    slide_index: int
    title: str
    script: str
    target_chars: int
    style: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PPTGenerationInput:
    """用户生成 PPT 的输入参数"""
    topic: str
    purpose: str
    audience: str
    slide_count: int
    style: str
    extra_notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceContext:
    """参考 PPT 的结构分析结果"""
    slide_count: int
    slides_summary: list[dict]  # [{"index": 1, "title": "...", "body_preview": "..."}]
    company_name: str = ""
    theme_colors: list[str] = field(default_factory=list)  # 主色列表, e.g. ["1A478A", "2E86AB"]
    font_name: str = ""
    style_notes: str = ""  # LLM 可读的风格描述
    asset_dir: str = ""
    logo_path: str = ""
    background_image_path: str = ""
    image_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PPTOutlineItem:
    """大纲中的一页"""
    slide_index: int
    title: str
    purpose: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GeneratedSlideContent:
    """AI 生成的单页 PPT 内容"""
    slide_index: int
    title: str
    bullets: list[str]
    speaker_hint: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GeneratedPPTResult:
    """一次 PPT 生成的完整结果"""
    input: PPTGenerationInput
    outline: list[PPTOutlineItem]
    slides: list[GeneratedSlideContent]
    pptx_path: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
