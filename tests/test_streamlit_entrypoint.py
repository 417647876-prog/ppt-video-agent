import subprocess
import sys
from pathlib import Path


def test_streamlit_entrypoint_can_import_app_package_without_project_root_on_path():
    project_root = Path(__file__).resolve().parents[1]
    script_path = project_root / "app" / "streamlit_app.py"
    code = (
        "import runpy, sys;"
        f"project_root = {str(project_root)!r};"
        "sys.path = [p for p in sys.path if p not in ('', project_root)];"
        f"runpy.run_path({str(script_path)!r}, run_name='__streamlit_test__')"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=project_root / "app",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
