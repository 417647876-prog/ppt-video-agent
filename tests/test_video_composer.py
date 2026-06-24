from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.video_composer import compose_slide_to_clip, concat_clips


def _make_fake_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fake content")


@pytest.fixture
def mock_ffmpeg():
    """Mock 所有 ffmpeg 调用，且让输出文件存在。"""
    def _run_side_effect(*args, **kwargs):
        # 从 cmd 参数中找出输出文件路径并创建
        cmd = args[0]
        for arg in cmd:
            if isinstance(arg, str) and arg.endswith(".mp4"):
                Path(arg).write_text("fake mp4")
                break
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    with patch("app.video_composer._get_ffmpeg_path", return_value="C:\\ffmpeg.exe"):
        with patch("app.video_composer.subprocess.run", side_effect=_run_side_effect):
            yield


def test_compose_slide_to_clip_runs_ffmpeg(mock_ffmpeg, tmp_path: Path):
    img = tmp_path / "slide_001.png"
    audio = tmp_path / "slide_001.wav"
    output = tmp_path / "clip_001.mp4"

    _make_fake_file(img)
    _make_fake_file(audio)

    # 不应抛异常
    compose_slide_to_clip(img, audio, output)
    assert output.exists()


def test_concat_clips_runs_ffmpeg(mock_ffmpeg, tmp_path: Path):
    clips = [tmp_path / "clip_001.mp4", tmp_path / "clip_002.mp4"]
    output = tmp_path / "final.mp4"

    for c in clips:
        _make_fake_file(c)

    concat_clips(clips, output)
    assert output.exists()
    # 验证 concat 文件被清理
    assert not (output.with_suffix(".concat.txt")).exists()
