from pathlib import Path
from zipfile import ZipFile

from app.audio_storage import build_audio_zip_bytes, build_file_zip_bytes


def test_build_audio_zip_bytes_keeps_file_names(tmp_path: Path):
    first = tmp_path / "slide_001.mp3"
    second = tmp_path / "slide_002.mp3"
    first.write_bytes(b"first-audio")
    second.write_bytes(b"second-audio")

    payload = build_audio_zip_bytes([first, second])
    zip_path = tmp_path / "audio.zip"
    zip_path.write_bytes(payload)

    with ZipFile(zip_path) as archive:
        assert archive.namelist() == ["slide_001.mp3", "slide_002.mp3"]
        assert archive.read("slide_001.mp3") == b"first-audio"


def test_build_file_zip_bytes_can_package_images(tmp_path: Path):
    first = tmp_path / "slide_001.png"
    second = tmp_path / "slide_002.png"
    first.write_bytes(b"first-image")
    second.write_bytes(b"second-image")

    payload = build_file_zip_bytes([first, second])
    zip_path = tmp_path / "images.zip"
    zip_path.write_bytes(payload)

    with ZipFile(zip_path) as archive:
        assert archive.namelist() == ["slide_001.png", "slide_002.png"]
        assert archive.read("slide_002.png") == b"second-image"
