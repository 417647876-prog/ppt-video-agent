from __future__ import annotations

import pytest

from app.models import (
    GeneratedSlideContent,
    PPTGenerationInput,
    PPTOutlineItem,
)
from app.ppt_content_generator import generate_content


class FakeLLMClient:
    def __init__(self, response: str = ""):
        self.response = response

    def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        if callable(self.response):
            return self.response(system_prompt, user_prompt)
        return self.response


_VALID_JSON = """{
  "slides": [
    {
      "slide_index": 1,
      "title": "封面",
      "bullets": ["核心内容概述", "本次培训目标", "整体框架"],
      "speaker_hint": "开场介绍整体框架"
    },
    {
      "slide_index": 2,
      "title": "背景分析",
      "bullets": ["市场现状", "核心痛点", "机会分析"],
      "speaker_hint": "分析业务背景"
    }
  ]
}"""


@pytest.fixture
def sample_input() -> PPTGenerationInput:
    return PPTGenerationInput(
        topic="测试主题",
        purpose="内部培训",
        audience="开发人员",
        slide_count=2,
        style="专业正式",
        extra_notes="",
    )


@pytest.fixture
def sample_outline() -> list[PPTOutlineItem]:
    return [
        PPTOutlineItem(slide_index=1, title="封面", purpose="开场"),
        PPTOutlineItem(slide_index=2, title="背景分析", purpose="分析背景"),
    ]


def test_generate_content_returns_slide_contents(sample_input, sample_outline):
    fake = FakeLLMClient(response=_VALID_JSON)
    result = generate_content(sample_input, sample_outline, fake)
    assert len(result) == 2
    assert all(isinstance(sc, GeneratedSlideContent) for sc in result)


def test_generate_content_has_correct_bullets(sample_input, sample_outline):
    fake = FakeLLMClient(response=_VALID_JSON)
    result = generate_content(sample_input, sample_outline, fake)
    assert result[0].title == "封面"
    assert len(result[0].bullets) == 3
    assert "核心内容概述" in result[0].bullets


def test_generate_content_raises_on_page_count_mismatch(sample_input, sample_outline):
    wrong_json = '{"slides": [{"slide_index": 1, "title": "T", "bullets": ["A"], "speaker_hint": ""}]}'
    fake = FakeLLMClient(response=wrong_json)
    with pytest.raises(ValueError, match="2 页"):
        generate_content(sample_input, sample_outline, fake)


def test_generate_content_strips_markdown_fence(sample_input, sample_outline):
    fake = FakeLLMClient(response="```json\n" + _VALID_JSON + "\n```")
    result = generate_content(sample_input, sample_outline, fake)
    assert len(result) == 2


def test_generate_content_falls_back_to_outline_title(sample_input, sample_outline):
    no_title_json = """{
      "slides": [
        {"slide_index": 1, "title": "", "bullets": ["A"], "speaker_hint": ""},
        {"slide_index": 2, "title": "", "bullets": ["B"], "speaker_hint": ""}
      ]
    }"""
    fake = FakeLLMClient(response=no_title_json)
    result = generate_content(sample_input, sample_outline, fake)
    assert result[0].title == "封面"
    assert result[1].title == "背景分析"
