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
