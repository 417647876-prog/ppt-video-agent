from __future__ import annotations

import subprocess
from pathlib import Path


def _get_ffmpeg_path() -> str:
    """查找 PATH 或默认安装位置的 ffmpeg。"""
    import shutil
    path = shutil.which("ffmpeg")
    if path:
        return path

    # 常见默认安装路径（Windows）
    candidates = [
        Path.home() / "ffmpeg" / "ffmpeg-7.0-full_build" / "bin" / "ffmpeg.exe",
        Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    raise FileNotFoundError(
        "未找到 ffmpeg，请从 https://ffmpeg.org/download.html 下载并添加到 PATH，"
        "或解压到 C:\\Users\\<用户名>\\ffmpeg\\bin\\"
    )


def compose_slide_to_clip(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    ffmpeg_path: str | None = None,
) -> None:
    if ffmpeg_path is None:
        ffmpeg_path = _get_ffmpeg_path()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_path,
        "-y",
        "-loop", "1",
        "-i", str(image_path.resolve()),
        "-i", str(audio_path.resolve()),
        "-c:v", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path.resolve()),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 合成失败（返回码 {result.returncode}）：{result.stderr.strip()}"
        )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("ffmpeg 未生成有效视频文件。")


def concat_clips(
    clip_paths: list[Path],
    output_path: Path,
    ffmpeg_path: str | None = None,
) -> None:
    if ffmpeg_path is None:
        ffmpeg_path = _get_ffmpeg_path()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    list_path = output_path.with_suffix(".concat.txt")
    lines = [f"file '{clip.resolve()}'" for clip in clip_paths]
    list_path.write_text("\n".join(lines), encoding="utf-8")

    try:
        cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path.resolve()),
            "-c", "copy",
            str(output_path.resolve()),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg 拼接失败（返回码 {result.returncode}）：{result.stderr.strip()}"
            )
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("ffmpeg 未生成有效拼接视频。")
    finally:
        list_path.unlink(missing_ok=True)
