from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# 在 import app.ppt_exporter 之前 mock 掉 win32com，确保两层模块关系正确
_mock_win32com = MagicMock()
_mock_win32com_client = MagicMock()
_mock_win32com.client = _mock_win32com_client
sys.modules["win32com"] = _mock_win32com
sys.modules["win32com.client"] = _mock_win32com_client

from app.models import SlideContent
from app.ppt_exporter import export_slides_to_images


@pytest.fixture
def sample_slides():
    return [
        SlideContent(index=1, title="页1", body="正文1", raw_text="页1\n正文1"),
        SlideContent(index=2, title="页2", body="正文2", raw_text="页2\n正文2"),
    ]


def test_export_slides_to_images_returns_image_paths(
    tmp_path: Path, sample_slides: list[SlideContent]
):
    pptx_path = tmp_path / "test.pptx"
    pptx_path.write_text("fake pptx content")
    output_dir = tmp_path / "images"

    mock_slide1 = MagicMock()
    mock_slide2 = MagicMock()

    def _export1(path, fmt):
        (output_dir / "slide_001.png").write_text("png1")

    def _export2(path, fmt):
        (output_dir / "slide_002.png").write_text("png2")

    mock_slide1.Export.side_effect = _export1
    mock_slide2.Export.side_effect = _export2

    mock_presentations = MagicMock()
    mock_presentation = MagicMock()
    mock_presentation.Slides.side_effect = lambda idx: (
        mock_slide1 if idx == 1 else mock_slide2
    )
    mock_presentations.Open.return_value = mock_presentation

    mock_app = MagicMock()
    mock_app.Presentations = mock_presentations

    _mock_win32com_client.Dispatch.return_value = mock_app

    result = export_slides_to_images(pptx_path, sample_slides, output_dir)

    mock_presentations.Open.assert_called_once_with(
        str(pptx_path.resolve()), WithWindow=False
    )
    mock_slide1.Export.assert_called_once_with(
        str(output_dir / "slide_001.png"), "PNG"
    )
    mock_slide2.Export.assert_called_once_with(
        str(output_dir / "slide_002.png"), "PNG"
    )

    assert len(result) == 2
    assert result[0].read_text() == "png1"
    assert mock_app.Quit.called


def test_export_raises_when_pptx_not_found(tmp_path: Path, sample_slides):
    missing = tmp_path / "missing.pptx"
    with pytest.raises(FileNotFoundError, match="PPT 文件不存在"):
        export_slides_to_images(missing, sample_slides, tmp_path)
