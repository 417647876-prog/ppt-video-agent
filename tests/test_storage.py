from pathlib import Path

from app.models import SlideContent, SlideScript
from app.storage import save_json, to_json_bytes


def test_to_json_bytes_serializes_dataclasses_as_utf8_json():
    slides = [
        SlideContent(index=1, title="标题", body="正文", raw_text="标题\n正文"),
    ]

    payload = to_json_bytes(slides)

    assert b"\xe6\xa0\x87\xe9\xa2\x98" in payload
    assert payload.decode("utf-8").startswith("[")


def test_save_json_writes_parent_directory(tmp_path: Path):
    scripts = [
        SlideScript(
            slide_index=1,
            title="第一页",
            script="这里是讲稿。",
            target_chars=220,
            style="course",
        )
    ]
    output = tmp_path / "nested" / "scripts.json"

    save_json(output, scripts)

    assert output.exists()
    assert "这里是讲稿" in output.read_text(encoding="utf-8")
