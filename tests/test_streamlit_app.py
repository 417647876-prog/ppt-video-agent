from app.streamlit_app import TTS_ENGINE_LABELS, create_tts_client, get_voice_options
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
