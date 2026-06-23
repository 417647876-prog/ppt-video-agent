from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Protocol, Sequence

from app.models import SlideScript


VOICE_OPTIONS: dict[str, str] = {
    "zh-CN-XiaoxiaoNeural": "晓晓 - 女声",
    "zh-CN-YunxiNeural": "云希 - 男声",
}


class TTSClientProtocol(Protocol):
    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        ...


class EdgeTTSClient:
    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        last_error = ""
        for _ in range(3):
            output_path.unlink(missing_ok=True)
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "edge-tts",
                    "--voice",
                    voice,
                    "--text",
                    " ".join(text.split()),
                    "--write-media",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
            last_error = result.stderr.strip()
            if output_path.exists() and output_path.stat().st_size > 0:
                return

        raise RuntimeError(last_error or "edge-tts 未生成有效音频文件。")


async def generate_audio_files(
    scripts: Sequence[SlideScript],
    voice: str,
    output_dir: Path,
    tts_client: TTSClientProtocol,
) -> list[Path]:
    if not scripts:
        raise ValueError("没有可生成语音的讲稿。")
    if voice not in VOICE_OPTIONS:
        raise ValueError(f"未知语音：{voice}")

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_paths: list[Path] = []

    for script in scripts:
        output_path = output_dir / f"slide_{script.slide_index:03d}.mp3"
        await tts_client.synthesize_to_file(script.script, voice, output_path)
        audio_paths.append(output_path)

    return audio_paths
