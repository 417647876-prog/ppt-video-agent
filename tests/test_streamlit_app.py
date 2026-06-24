from app.models import SlideContent, SlideScript
from app.streamlit_app import (
    TTS_ENGINE_LABELS,
    create_tts_client,
    generate_script_preview,
    get_voice_options,
)
from app.tts_client import EdgeTTSClient, MiniMaxTTSClient, WindowsSapiTTSClient


def test_get_voice_options_uses_minimax_by_default():
    options = get_voice_options("minimax")

    assert "female-tianmei" in options


def test_create_tts_client_supports_minimax_and_windows():
    assert isinstance(create_tts_client("minimax"), MiniMaxTTSClient)
    assert isinstance(create_tts_client("windows"), WindowsSapiTTSClient)


def test_edge_tts_is_available_from_streamlit_options():
    options = get_voice_options("edge")

    assert "zh-CN-XiaoxiaoNeural" in options
    assert isinstance(create_tts_client("edge"), EdgeTTSClient)


def test_volcengine_is_hidden_from_voice_engine_selector():
    assert "volcengine" not in TTS_ENGINE_LABELS


def test_generate_script_preview_parses_ppt_and_generates_scripts(monkeypatch, tmp_path):
    pptx_path = tmp_path / "demo.pptx"
    pptx_path.write_bytes(b"fake pptx")
    parsed_slides = [
        SlideContent(index=1, title="标题", body="正文", raw_text="第一页内容"),
        SlideContent(index=2, title="第二页", body="正文", raw_text="第二页内容"),
    ]
    generated_scripts = [
        SlideScript(
            slide_index=1,
            title="标题",
            script="第一页讲稿",
            target_chars=220,
            style="course",
        ),
        SlideScript(
            slide_index=2,
            title="第二页",
            script="第二页讲稿",
            target_chars=220,
            style="course",
        ),
    ]

    monkeypatch.setattr("app.streamlit_app.parse_pptx", lambda path: parsed_slides)
    monkeypatch.setattr(
        "app.streamlit_app.generate_scripts",
        lambda **kwargs: generated_scripts,
    )

    slides, scripts = generate_script_preview(
        pptx_path=pptx_path,
        total_minutes=30,
        style_key="course",
        custom_style="通俗一些",
        llm_client=object(),
        debug_mode=False,
    )

    assert slides == parsed_slides
    assert scripts == generated_scripts


def test_generate_script_preview_debug_mode_limits_to_first_slide(monkeypatch, tmp_path):
    pptx_path = tmp_path / "demo.pptx"
    pptx_path.write_bytes(b"fake pptx")
    parsed_slides = [
        SlideContent(index=1, title="标题", body="正文", raw_text="第一页内容"),
        SlideContent(index=2, title="第二页", body="正文", raw_text="第二页内容"),
    ]
    calls = []

    monkeypatch.setattr("app.streamlit_app.parse_pptx", lambda path: parsed_slides)
    monkeypatch.setattr(
        "app.streamlit_app.generate_scripts",
        lambda **kwargs: calls.append(kwargs) or [],
    )

    generate_script_preview(
        pptx_path=pptx_path,
        total_minutes=30,
        style_key="course",
        custom_style="",
        llm_client=object(),
        debug_mode=True,
    )

    assert calls[0]["slides"] == parsed_slides[:1]
    assert calls[0]["total_minutes"] == 3
