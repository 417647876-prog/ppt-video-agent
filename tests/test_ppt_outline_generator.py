from __future__ import annotations

import pytest

from app.models import PPTGenerationInput, PPTOutlineItem, ReferenceContext
from app.ppt_outline_generator import generate_outline, generate_outline_with_reference


class FakeLLMClient:
    def __init__(self, response: str = ""):
        self.last_system_prompt = ""
        self.last_user_prompt = ""
        self.response = response
        self.call_count = 0

    def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        self.call_count += 1
        if callable(self.response):
            return self.response(system_prompt, user_prompt)
        return self.response


_VALID_JSON = """[
  {"slide_index": 1, "title": "封面", "purpose": "开场介绍主题"},
  {"slide_index": 2, "title": "背景分析", "purpose": "分析业务背景"},
  {"slide_index": 3, "title": "核心方案", "purpose": "介绍核心方案"}
]"""


@pytest.fixture
def sample_input() -> PPTGenerationInput:
    return PPTGenerationInput(
        topic="测试主题",
        purpose="内部培训",
        audience="开发人员",
        slide_count=3,
        style="专业正式",
        extra_notes="无",
    )


def test_generate_outline_returns_outline_items(sample_input):
    fake = FakeLLMClient(response=_VALID_JSON)
    result = generate_outline(sample_input, fake)
    assert len(result) == 3
    assert all(isinstance(item, PPTOutlineItem) for item in result)
    assert fake.call_count == 1
    assert "测试主题" in fake.last_user_prompt


def test_generate_outline_contains_slide_count_in_prompt(sample_input):
    fake = FakeLLMClient(response=_VALID_JSON)
    generate_outline(sample_input, fake)
    assert "3 页" in fake.last_user_prompt


def test_generate_outline_with_reference_uses_reference_context(sample_input):
    ref = ReferenceContext(
        slide_count=5,
        slides_summary=[
            {"index": 1, "title": "旧封面", "body_preview": "旧内容"},
        ],
    )
    fake = FakeLLMClient(response=_VALID_JSON)
    result = generate_outline_with_reference(sample_input, ref, fake)
    assert len(result) == 3
    assert "旧封面" in fake.last_user_prompt
    assert "5 页" in fake.last_user_prompt


def test_generate_outline_raises_on_empty_json(sample_input):
    fake = FakeLLMClient(response="[]")
    with pytest.raises(ValueError, match="无法解析"):
        generate_outline(sample_input, fake)


def test_generate_outline_raises_on_invalid_json(sample_input):
    fake = FakeLLMClient(response="不是 JSON")
    with pytest.raises(Exception):
        generate_outline(sample_input, fake)


def test_generate_outline_strips_markdown_code_fence(sample_input):
    fake = FakeLLMClient(response=f"```json\n{_VALID_JSON}\n```")
    result = generate_outline(sample_input, fake)
    assert len(result) == 3


def test_outline_items_have_correct_attributes(sample_input):
    fake = FakeLLMClient(response=_VALID_JSON)
    result = generate_outline(sample_input, fake)
    assert result[0].slide_index == 1
    assert result[0].title == "封面"
    assert result[0].purpose == "开场介绍主题"
