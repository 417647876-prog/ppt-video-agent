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


def test_from_env_prefers_project_dotenv_over_existing_environment(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("LLM_BASE_URL", "https://old.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "old-key")
    monkeypatch.setenv("LLM_MODEL", "old-model")
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            [
                "LLM_BASE_URL=https://api.deepseek.com",
                "LLM_API_KEY=new-key",
                "LLM_MODEL=deepseek-chat",
            ]
        ),
        encoding="utf-8",
    )

    config = OpenAICompatibleLLMClient.from_env(dotenv_path=dotenv_path).config

    assert config.base_url == "https://api.deepseek.com"
    assert config.api_key == "new-key"
    assert config.model == "deepseek-chat"
