import pytest

from app.llm_client import OpenAICompatibleLLMClient


def test_from_env_raises_clear_error_when_required_config_missing(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(ValueError) as exc_info:
        OpenAICompatibleLLMClient.from_env(load_dotenv_file=False)

    message = str(exc_info.value)
    assert "LLM_BASE_URL" in message
    assert "LLM_API_KEY" in message
    assert "LLM_MODEL" in message
