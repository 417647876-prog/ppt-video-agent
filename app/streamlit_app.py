from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.audio_storage import build_audio_zip_bytes
from app.llm_client import OpenAICompatibleLLMClient
from app.ppt_agent import build_agent
from app.ppt_exporter import export_slides_to_images
from app.ppt_parser import parse_pptx
from app.script_generator import STYLE_OPTIONS, generate_scripts
from app.storage import to_json_bytes
from app.tts_client import (
    MINIMAX_VOICE_OPTIONS,
    VOICE_OPTIONS,
    VOLC_ENGINE_VOICE_OPTIONS,
    WINDOWS_VOICE_OPTIONS,
    EdgeTTSClient,
    MiniMaxTTSClient,
    VolcengineTTSClient,
    WindowsSapiTTSClient,
    generate_audio_files,
)
from app.video_composer import compose_slide_to_clip, concat_clips


STYLE_LABELS = {
    "course": "课程讲解风格",
    "project_report": "项目汇报风格",
    "interview": "面试讲解风格",
    "sales_pitch": "销售路演风格",
}

TTS_ENGINE_LABELS = {
    "edge": "Edge 免费在线语音（MP3）",
    "minimax": "MiniMax 在线语音（自然，WAV）",
    "windows": "Windows 本机语音（稳定，WAV）",
}


def get_voice_options(tts_engine: str) -> dict[str, str]:
    if tts_engine == "edge":
        return VOICE_OPTIONS
    if tts_engine == "minimax":
        return MINIMAX_VOICE_OPTIONS
    if tts_engine == "volcengine":
        return VOLC_ENGINE_VOICE_OPTIONS
    if tts_engine == "windows":
        return WINDOWS_VOICE_OPTIONS
    raise ValueError(f"未知语音引擎：{tts_engine}")


def create_tts_client(tts_engine: str):
    if tts_engine == "edge":
        return EdgeTTSClient()
    if tts_engine == "minimax":
        return MiniMaxTTSClient()
    if tts_engine == "volcengine":
        return VolcengineTTSClient()
    if tts_engine == "windows":
        return WindowsSapiTTSClient()
    raise ValueError(f"未知语音引擎：{tts_engine}")


def _save_uploaded_file(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def generate_script_preview(
    pptx_path: Path,
    total_minutes: int,
    style_key: str,
    custom_style: str,
    llm_client,
    debug_mode: bool,
):
    slides = parse_pptx(pptx_path)
    if debug_mode:
        slides = slides[:1]
        total_minutes = min(int(total_minutes), 3)

    scripts = generate_scripts(
        slides=slides,
        total_minutes=int(total_minutes),
        style_key=style_key,
        custom_style=custom_style,
        llm_client=llm_client,
    )
    return slides, scripts


def main() -> None:
    st.set_page_config(page_title="AI PPT 演讲稿生成器", layout="wide")
    st.title("AI PPT 演讲视频生成器")

    uploaded_file = st.file_uploader("上传 PPT 文件", type=["pptx"])

    col1, col2 = st.columns(2)
    with col1:
        total_minutes = st.number_input("目标总时长（分钟）", min_value=1, value=30, step=1)
    with col2:
        style_key = st.selectbox(
            "讲稿风格",
            options=list(STYLE_OPTIONS.keys()),
            format_func=lambda key: STYLE_LABELS[key],
        )
    custom_style = st.text_area(
        "自定义风格补充说明（可选）",
        help="例如：用通俗、稳重、适合零基础学员的方式讲解。",
    )

    tts_engine = st.selectbox(
        "语音引擎",
        options=list(TTS_ENGINE_LABELS.keys()),
        format_func=lambda key: TTS_ENGINE_LABELS[key],
        index=0,
        key="tts_engine",
    )
    voice_options = get_voice_options(tts_engine)
    voice_keys = list(voice_options.keys())
    selected_voice = st.selectbox(
        "选择语音",
        options=voice_keys,
        format_func=lambda key: f"{key} - {voice_options[key]}",
        index=0,
        key=f"selected_voice_{tts_engine}",
    )

    debug_mode = st.checkbox("调试模式（仅前 2 页，缩短时间）", value=True)

    if uploaded_file is None:
        st.info("请先上传一个 .pptx 文件。")
        return

    preview_col, video_col = st.columns(2)
    with preview_col:
        preview_clicked = st.button("先生成演讲稿预览", use_container_width=True)
    with video_col:
        video_clicked = st.button("一键生成视频", type="primary", use_container_width=True)

    if preview_clicked:
        try:
            pptx_path = _save_uploaded_file(uploaded_file)
            progress = st.progress(0, text="正在解析 PPT...")
            progress.progress(20, text="正在解析 PPT...")

            llm_client = OpenAICompatibleLLMClient.from_env()
            progress.progress(50, text="正在调用 LLM 生成讲稿...")
            slides, scripts = generate_script_preview(
                pptx_path=pptx_path,
                total_minutes=int(total_minutes),
                style_key=style_key,
                custom_style=custom_style,
                llm_client=llm_client,
                debug_mode=debug_mode,
            )

            progress.progress(100, text="讲稿生成完成！")
            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
            st.session_state["pptx_path"] = str(pptx_path)
            st.session_state.pop("image_paths", None)
            st.session_state.pop("final_video_path", None)
            st.session_state.pop("saved_video_path", None)
            st.success("讲稿已生成，可以先在下方预览。")
        except Exception as exc:
            st.error(str(exc))

    if video_clicked:
        try:
            pptx_path = _save_uploaded_file(uploaded_file)
            progress = st.progress(0, text="正在解析 PPT...")

            progress.progress(5, text="正在解析 PPT...")
            llm_client = OpenAICompatibleLLMClient.from_env()
            progress.progress(15, text="正在调用 LLM 生成讲稿...")
            slides, scripts = generate_script_preview(
                pptx_path=pptx_path,
                total_minutes=int(total_minutes),
                style_key=style_key,
                custom_style=custom_style,
                llm_client=llm_client,
                debug_mode=debug_mode,
            )

            progress.progress(35, text="正在生成语音...")
            audio_dir = Path(tempfile.mkdtemp(prefix="ppt_audio_"))
            tts_client = create_tts_client(tts_engine)
            audio_paths = asyncio.run(
                generate_audio_files(
                    scripts=scripts,
                    voice=selected_voice,
                    output_dir=audio_dir,
                    tts_client=tts_client,
                )
            )

            progress.progress(55, text="正在导出 PPT 页面图片...")
            image_dir = Path(tempfile.mkdtemp(prefix="ppt_images_"))
            image_paths = export_slides_to_images(pptx_path, slides, image_dir)

            progress.progress(70, text="正在合成视频片段...")
            video_dir = Path(tempfile.mkdtemp(prefix="ppt_video_"))
            clip_paths = []
            for i, (img, audio) in enumerate(zip(image_paths, audio_paths)):
                clip = video_dir / f"clip_{i+1:03d}.mp4"
                compose_slide_to_clip(img, audio, clip)
                clip_paths.append(clip)
                pct = 70 + int((i + 1) / len(image_paths) * 25)
                progress.progress(pct, text=f"已合成第 {i+1}/{len(image_paths)} 页...")

            progress.progress(96, text="正在拼接最终视频...")
            final_path = video_dir / "final.mp4"
            concat_clips(clip_paths, final_path)

            # 保存到项目 output 目录
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_path = output_dir / f"{uploaded_file.name}_script_{style_key}_voice_{tts_engine}_{selected_voice}_{timestamp}.mp4"
            import shutil
            shutil.copy2(str(final_path), str(saved_path))

            progress.progress(100, text="完成！")

            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
            st.session_state["pptx_path"] = str(pptx_path)
            st.session_state["image_paths"] = image_paths
            st.session_state["final_video_path"] = str(final_path)
            st.session_state["saved_video_path"] = str(saved_path)

            st.success("视频生成完成！" + ("（调试模式-仅前2页）" if debug_mode else ""))
            st.balloons()
        except Exception as exc:
            st.error(str(exc))

    slides = st.session_state.get("slides", [])
    scripts = st.session_state.get("scripts", [])
    if not slides or not scripts:
        return

    st.subheader("讲稿预览")
    for slide, script in zip(slides, scripts):
        title = slide.title or "无标题"
        with st.expander(f"第 {slide.index} 页：{title}", expanded=False):
            left, right = st.columns(2)
            with left:
                st.markdown("**PPT 原文**")
                st.text(slide.raw_text)
            with right:
                st.markdown("**AI 讲稿**")
                st.write(script.script)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.download_button(
            "下载 slides.json", data=to_json_bytes(slides),
            file_name="slides.json", mime="application/json",
        )
    with col_b:
        st.download_button(
            "下载 scripts.json", data=to_json_bytes(scripts),
            file_name="scripts.json", mime="application/json",
        )

    image_paths = st.session_state.get("image_paths", [])
    final_video_path = st.session_state.get("final_video_path")

    if image_paths:
        st.subheader("页面图片预览")
        for img in image_paths:
            page_num = img.stem.split("_")[-1].lstrip("0") or "0"
            st.image(str(img), caption=f"第 {page_num} 页", use_column_width=True)

    if final_video_path:
        st.subheader("最终视频")
        with open(final_video_path, "rb") as f:
            video_bytes = f.read()
        st.video(video_bytes)
        with col_c:
            st.download_button(
                "下载 final.mp4", data=video_bytes,
                file_name="final.mp4", mime="video/mp4",
            )


if __name__ == "__main__":
    main()



