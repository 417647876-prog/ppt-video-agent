from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langgraph.graph import StateGraph, add_messages

from app.audio_storage import build_audio_zip_bytes
from app.llm_client import OpenAICompatibleLLMClient
from app.models import SlideContent, SlideScript
from app.ppt_exporter import export_slides_to_images
from app.ppt_parser import parse_pptx
from app.script_generator import generate_scripts
from app.tts_client import WindowsSapiTTSClient, generate_audio_files
from app.video_composer import compose_slide_to_clip, concat_clips


class AgentState(TypedDict):
    """Agent 工作流的状态。"""
    pptx_path: str
    total_minutes: int
    style_key: str
    custom_style: str
    slides: list[SlideContent]
    scripts: list[SlideScript]
    audio_dir: str
    audio_paths: list[str]
    image_dir: str
    image_paths: list[str]
    video_dir: str
    final_video: str
    messages: Annotated[list, add_messages]
    error: str


def node_parse_pptx(state: AgentState) -> dict:
    pptx = Path(state["pptx_path"])
    slides = parse_pptx(pptx)
    return {"slides": slides}


def node_generate_scripts(state: AgentState) -> dict:
    client = OpenAICompatibleLLMClient.from_env()
    scripts = generate_scripts(
        slides=state["slides"],
        total_minutes=state["total_minutes"],
        style_key=state["style_key"],
        custom_style=state.get("custom_style", ""),
        llm_client=client,
    )
    return {"scripts": scripts}


async def _generate_audio(slides, scripts):
    audio_dir = Path(tempfile.mkdtemp(prefix="ppt_audio_"))
    tts = WindowsSapiTTSClient()
    paths = await generate_audio_files(
        scripts=scripts,
        voice="Microsoft Huihui Desktop",
        output_dir=audio_dir,
        tts_client=tts,
    )
    return str(audio_dir), [str(p) for p in paths]


def node_generate_audio(state: AgentState) -> dict:
    result = asyncio.run(_generate_audio(state["slides"], state["scripts"]))
    return {"audio_dir": result[0], "audio_paths": result[1]}


def node_export_images(state: AgentState) -> dict:
    pptx = Path(state["pptx_path"])
    image_dir = Path(tempfile.mkdtemp(prefix="ppt_images_"))
    paths = export_slides_to_images(pptx, state["slides"], image_dir)
    return {"image_dir": str(image_dir), "image_paths": [str(p) for p in paths]}


def node_compose_video(state: AgentState) -> dict:
    video_dir = Path(tempfile.mkdtemp(prefix="ppt_video_"))
    image_paths = [Path(p) for p in state["image_paths"]]
    audio_paths = [Path(p) for p in state["audio_paths"]]

    clips: list[Path] = []
    for img, audio in zip(image_paths, audio_paths):
        clip = video_dir / f"clip_{len(clips)+1:03d}.mp4"
        compose_slide_to_clip(img, audio, clip)
        clips.append(clip)

    final_path = video_dir / "final.mp4"
    concat_clips(clips, final_path)
    return {"video_dir": str(video_dir), "final_video": str(final_path)}


def build_agent() -> StateGraph:
    """构建 LangGraph 工作流。"""
    builder = StateGraph(AgentState)

    builder.add_node("parse_pptx", node_parse_pptx)
    builder.add_node("generate_scripts", node_generate_scripts)
    builder.add_node("generate_audio", node_generate_audio)
    builder.add_node("export_images", node_export_images)
    builder.add_node("compose_video", node_compose_video)

    builder.set_entry_point("parse_pptx")
    builder.add_edge("parse_pptx", "generate_scripts")
    builder.add_edge("generate_scripts", "generate_audio")
    builder.add_edge("generate_audio", "export_images")
    builder.add_edge("export_images", "compose_video")

    return builder.compile()
