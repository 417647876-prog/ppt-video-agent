from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from app.models import SlideContent, SlideScript

# mock win32com
_mock_win32com = MagicMock()
_mock_win32com_client = MagicMock()
_mock_win32com.client = _mock_win32com_client
sys.modules["win32com"] = _mock_win32com
sys.modules["win32com.client"] = _mock_win32com_client

from app.ppt_agent import build_agent, node_parse_pptx, node_generate_scripts


def test_agent_graph_structure():
    graph = build_agent()
    nodes = {n for n in graph.nodes if not n.startswith("_")}
    expected = {"parse_pptx", "generate_scripts", "generate_audio",
                "export_images", "compose_video"}
    assert nodes == expected


def test_agent_node_parse_pptx():
    slide = SlideContent(index=1, title="Test", body="Body", raw_text="Test\nBody")
    with patch("app.ppt_agent.parse_pptx", return_value=[slide]):
        result = node_parse_pptx({"pptx_path": "test.pptx"})
    assert result["slides"] == [slide]


def test_agent_node_generate_scripts():
    slide = SlideContent(index=1, title="Test", body="Body", raw_text="Test\nBody")
    script = SlideScript(slide_index=1, title="Test", script="Script", target_chars=100, style="course")
    mock_client = MagicMock()
    with patch("app.ppt_agent.OpenAICompatibleLLMClient", return_value=mock_client):
        with patch("app.ppt_agent.generate_scripts", return_value=[script]):
            result = node_generate_scripts({
                "slides": [slide], "total_minutes": 30,
                "style_key": "course", "custom_style": "",
            })
    assert result["scripts"][0].script == "Script"
