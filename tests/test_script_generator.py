from app.models import SlideContent
from app.script_generator import build_prompt, calculate_target_chars, generate_scripts


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        assert "第一页标题" in prompt
        return "这是一段由测试客户端返回的讲稿。"


def test_calculate_target_chars_uses_total_minutes_and_slide_count():
    assert calculate_target_chars(total_minutes=120, slide_count=60) == 460


def test_calculate_target_chars_never_returns_zero():
    assert calculate_target_chars(total_minutes=1, slide_count=60) == 10


def test_build_prompt_contains_style_slide_text_and_target_length():
    slide = SlideContent(
        index=1,
        title="第一页标题",
        body="第一页正文",
        raw_text="第一页标题\n第一页正文",
    )

    prompt = build_prompt(
        slide=slide,
        target_chars=440,
        style_key="course",
        custom_style="适合零基础学员。",
    )

    assert "课程讲解风格" in prompt
    assert "适合零基础学员" in prompt
    assert "第一页标题" in prompt
    assert "第一页正文" in prompt
    assert "440" in prompt


def test_generate_scripts_calls_llm_and_returns_slide_scripts():
    slides = [
        SlideContent(
            index=1,
            title="第一页标题",
            body="第一页正文",
            raw_text="第一页标题\n第一页正文",
        )
    ]

    scripts = generate_scripts(
        slides=slides,
        total_minutes=2,
        style_key="course",
        custom_style="",
        llm_client=FakeLLMClient(),
    )

    assert len(scripts) == 1
    assert scripts[0].slide_index == 1
    assert scripts[0].script == "这是一段由测试客户端返回的讲稿。"
    assert scripts[0].style == "course"
