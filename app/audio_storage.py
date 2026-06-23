from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def build_audio_zip_bytes(audio_paths: list[Path]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in audio_paths:
            archive.write(path, arcname=path.name)
    return buffer.getvalue()
