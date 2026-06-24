from pathlib import Path

import pytest

from app.models import SlideScript
from app.tts_client import VOICE_OPTIONS, WINDOWS_VOICE_OPTIONS, generate_audio_files


class FakeTTSClient:
    file_extension = "wav"

    def __init__(self):
        self.calls = []

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        self.calls.append((text, voice, output_path))
        output_path.write_bytes(f"audio:{voice}:{text}".encode("utf-8"))


@pytest.mark.anyio
async def test_generate_audio_files_creates_one_audio_file_per_script(tmp_path: Path):
    scripts = [
        SlideScript(
            slide_index=1,
            title="第一页",
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
    client = FakeTTSClient()

    files = await generate_audio_files(
        scripts=scripts,
        voice="zh-CN-XiaoxiaoNeural",
        output_dir=tmp_path,
        tts_client=client,
    )

    assert [path.name for path in files] == ["slide_001.wav", "slide_002.wav"]
    assert files[0].read_bytes().startswith(b"audio:zh-CN-XiaoxiaoNeural")
    assert len(client.calls) == 2


def test_voice_options_include_default_chinese_voices():
    assert VOICE_OPTIONS["zh-CN-XiaoxiaoNeural"] == "晓晓 - 女声"
    assert VOICE_OPTIONS["zh-CN-YunxiNeural"] == "云希 - 男声"
    assert WINDOWS_VOICE_OPTIONS["Microsoft Huihui Desktop"] == "慧慧 - 女声（Windows 本机）"
def test_azure_voice_options_include_chinese_voices():
    from app.tts_client import AZURE_VOICE_OPTIONS
    assert "zh-CN-XiaoxiaoNeural" in AZURE_VOICE_OPTIONS
    assert "zh-CN-YunxiNeural" in AZURE_VOICE_OPTIONS
    assert len(AZURE_VOICE_OPTIONS) >= 10


def test_minimax_voice_options_include_voices():
    from app.tts_client import MINIMAX_VOICE_OPTIONS
    assert list(MINIMAX_VOICE_OPTIONS)[0] == "male-qn-jingying"
    assert "Chinese (Mandarin)_Humorous_Elder" in MINIMAX_VOICE_OPTIONS
    assert "Chinese (Mandarin)_Radio_Host" in MINIMAX_VOICE_OPTIONS
    assert "Chinese (Mandarin)_Gentleman" in MINIMAX_VOICE_OPTIONS
    assert "presenter_male" in MINIMAX_VOICE_OPTIONS
    assert "audiobook_male_1" in MINIMAX_VOICE_OPTIONS
    assert "female-chengshu" in MINIMAX_VOICE_OPTIONS
    assert "presenter_female" in MINIMAX_VOICE_OPTIONS
    assert "female-tianmei" in MINIMAX_VOICE_OPTIONS
    assert "female-shaonv" in MINIMAX_VOICE_OPTIONS
    assert "female-yujie" in MINIMAX_VOICE_OPTIONS
    assert "male-qn-qingse" in MINIMAX_VOICE_OPTIONS
    assert len(MINIMAX_VOICE_OPTIONS) >= 12


@pytest.mark.anyio
async def test_minimax_tts_writes_hex_encoded_audio(monkeypatch, tmp_path: Path):
    import httpx

    from app.tts_client import MiniMaxTTSClient

    wav_bytes = b"RIFF$\x00\x00\x00WAVEfmt "

    class FakeResponse:
        def json(self):
            return {
                "base_resp": {"status_code": 0},
                "data": {"audio": wav_bytes.hex()},
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    monkeypatch.setenv("MINIMAX_GROUP_ID", "test-group")
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    output_path = tmp_path / "slide_001.wav"

    await MiniMaxTTSClient().synthesize_to_file(
        "测试语音",
        "female-tianmei",
        output_path,
    )

    assert output_path.read_bytes() == wav_bytes


@pytest.mark.anyio
async def test_minimax_tts_uses_china_api_host_by_default(monkeypatch, tmp_path: Path):
    import httpx

    from app.tts_client import MiniMaxTTSClient

    requested_urls = []

    class FakeResponse:
        def json(self):
            return {
                "base_resp": {"status_code": 0},
                "data": {"audio": b"RIFF$\x00\x00\x00WAVEfmt ".hex()},
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, *args, **kwargs):
            requested_urls.append(url)
            return FakeResponse()

    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    monkeypatch.setenv("MINIMAX_GROUP_ID", "test-group")
    monkeypatch.delenv("MINIMAX_API_BASE_URL", raising=False)
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    await MiniMaxTTSClient().synthesize_to_file(
        "测试语音",
        "female-tianmei",
        tmp_path / "slide_001.wav",
    )

    assert requested_urls == ["https://api.minimax.chat/v1/t2a_v2"]


@pytest.mark.anyio
async def test_minimax_tts_loads_env_file_before_request(monkeypatch, tmp_path: Path):
    import httpx

    from app.tts_client import MiniMaxTTSClient

    wav_bytes = b"RIFF$\x00\x00\x00WAVEfmt "

    class FakeResponse:
        def json(self):
            return {
                "base_resp": {"status_code": 0},
                "data": {"audio": wav_bytes.hex()},
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_GROUP_ID", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "MINIMAX_API_KEY=test-key\nMINIMAX_GROUP_ID=test-group\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    output_path = tmp_path / "slide_001.wav"

    await MiniMaxTTSClient().synthesize_to_file(
        "测试语音",
        "female-tianmei",
        output_path,
    )

    assert output_path.read_bytes() == wav_bytes
