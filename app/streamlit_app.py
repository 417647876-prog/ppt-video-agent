from __future__ import annotations


import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.audio_storage import build_audio_zip_bytes, build_file_zip_bytes
from app.llm_client import OpenAICompatibleLLMClient
from app.ppt_outline_generator import generate_outline_with_reference
from app.ppt_template_analyzer import analyze_reference_pptx
from app.ppt_agent import build_agent
from app.ppt_exporter import export_slides_to_images
from app.ppt_parser import parse_pptx
from app.script_generator import STYLE_OPTIONS, build_prompt, generate_scripts
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
from app.video_composer import _get_ffmpeg_path, _get_ffprobe_path, compose_slide_to_clip, concat_clips


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

    # PPT 生成功能已暂停（代码仍保留在 app/ 目录）

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
            status = st.status("📄 解析 PPT...", expanded=True)
            progress = st.progress(0, text="正在解析 PPT...")
            progress.progress(20, text="正在解析 PPT...")

            llm_client = OpenAICompatibleLLMClient.from_env()
            status.update(label="🤖 生成讲稿...")
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
            status.update(label="✅ 讲稿生成完成", state="complete", expanded=False)
            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
            st.session_state["pptx_path"] = str(pptx_path)
            st.session_state.pop("image_paths", None)
            st.session_state.pop("audio_paths", None)
            st.session_state.pop("final_video_path", None)
            st.session_state.pop("saved_video_path", None)
            st.session_state.pop("scripts_edited", None)
            st.success("讲稿已生成，可以先在下方预览。")
        except Exception as exc:
            try:
                status.update(label="❌ 讲稿生成失败", state="error", expanded=True)
            except Exception:
                pass
            st.error(f"❌ 讲稿生成失败：{exc}")

    if video_clicked:
        current_stage = "视频生成"
        try:
            pptx_path = _save_uploaded_file(uploaded_file)
            status = st.status("📄 解析 PPT...", expanded=True)
            bar = st.progress(0, text="")
            page_text = st.empty()
            
            current_stage = "解析 PPT / 生成讲稿"
            if st.session_state.get("scripts") and st.session_state.get("slides"):
                slides = st.session_state["slides"]
                scripts = st.session_state["scripts"]
                status.update(label="✅ 使用已有讲稿（跳过 LLM 生成）", state="complete")
            else:
                bar.progress(10, text="正在解析 PPT...")
                llm_client = OpenAICompatibleLLMClient.from_env()
                slides, scripts = generate_script_preview(
                    pptx_path=pptx_path,
                    total_minutes=int(total_minutes),
                    style_key=style_key,
                    custom_style=custom_style,
                    llm_client=llm_client,
                    debug_mode=debug_mode,
                )
                status.update(label="✅ 解析 PPT + 生成讲稿完成", state="complete")
            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
            
            current_stage = "生成语音"
            status.update(label="🔊 生成语音...")
            bar.progress(35, text="正在生成语音...")
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
            bar.progress(55, text="语音生成完成")
            status.update(label="✅ 语音生成完成", state="complete")
            page_text.text("")

            current_stage = "导出页面图片"
            status.update(label="🖼️ 导出页面图片...")
            bar.progress(55, text="正在导出 PPT 页面图片...")
            image_dir = Path(tempfile.mkdtemp(prefix="ppt_images_"))
            image_paths = export_slides_to_images(pptx_path, slides, image_dir)
            bar.progress(70, text="导出页面图片完成")
            status.update(label="✅ 导出页面图片完成", state="complete")

            current_stage = "合成视频片段"
            status.update(label="🎬 合成视频片段...")
            bar.progress(70, text="正在合成视频片段...")
            video_dir = Path(tempfile.mkdtemp(prefix="ppt_video_"))
            clip_paths = []
            for i, (img, audio) in enumerate(zip(image_paths, audio_paths)):
                clip = video_dir / f"clip_{i+1:03d}.mp4"
                compose_slide_to_clip(img, audio, clip)
                clip_paths.append(clip)
                pct = 70 + int((i + 1) / len(image_paths) * 25)
                bar.progress(pct)
                page_text.text(f"合成第 {i+1}/{len(image_paths)} 页")
            bar.progress(96, text="合成完成")
            status.update(label="✅ 合成视频片段完成", state="complete")

            current_stage = "拼接最终视频"
            status.update(label="🔗 拼接最终视频...")
            bar.progress(96, text="正在拼接最终视频...")
            final_path = video_dir / "final.mp4"
            concat_clips(clip_paths, final_path)
            bar.progress(100, text="完成！")

            current_stage = "保存最终视频"
            # 保存到项目 output 目录
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_path = output_dir / f"{uploaded_file.name}_script_{style_key}_voice_{tts_engine}_{selected_voice}_{timestamp}.mp4"
            import shutil
            shutil.copy2(str(final_path), str(saved_path))

            status.update(label="✅ 视频生成完成！🎉", state="complete", expanded=False)

            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
            st.session_state["pptx_path"] = str(pptx_path)
            st.session_state["audio_paths"] = audio_paths
            st.session_state["image_paths"] = image_paths
            st.session_state["final_video_path"] = str(final_path)
            st.session_state["saved_video_path"] = str(saved_path)

            st.success("视频生成完成！" + ("（调试模式-仅前2页）" if debug_mode else ""))
            st.balloons()

            current_stage = "读取视频时长"
            # 显示实际时长对比
            ffprobe_path = _get_ffprobe_path(_get_ffmpeg_path())
            dur_result = subprocess.run(
                [ffprobe_path, "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(final_path)],
                capture_output=True, text=True,
            )
            if dur_result.stdout.strip():
                actual_sec = float(dur_result.stdout.strip())
                actual_min = round(actual_sec / 60, 1)
                diff = round(actual_min - int(total_minutes), 1)
                diff_text = f"（比目标{'多' if diff > 0 else '少'} {abs(diff):.1f} 分钟）" if abs(diff) > 0.5 else "（与目标基本一致）"
                st.info(f"⏱️ 实际视频时长：{actual_min} 分钟（目标：{int(total_minutes)} 分钟）{diff_text}")
        except Exception as exc:
            try:
                status.update(label="❌ 生成失败", state="error", expanded=True)
                bar.progress(0, text="")
            except Exception:
                pass  # status or bar not created yet
            st.error(f"❌ {current_stage}失败：{exc}")

    slides = st.session_state.get("slides", [])
    scripts = st.session_state.get("scripts", [])
    if not slides or not scripts:
        return

    st.subheader("讲稿预览")
    for slide, script in zip(slides, scripts):
        title = slide.title or "无标题"
        edit_badge = " ✏️" if st.session_state.get("scripts_edited") else ""
        with st.expander(f"第 {slide.index} 页：{title}{edit_badge}", expanded=False):
            left, right = st.columns(2)
            with left:
                st.markdown("**PPT 原文**")
                st.text(slide.raw_text)
            with right:
                st.markdown("**AI 讲稿（点击下方文本框编辑）**")
                st.text_area(
                    label=f"编辑第{slide.index}页讲稿",
                    value=script.script,
                    height=200,
                    key=f"script_edit_{slide.index}",
                    label_visibility="collapsed",
                )
                if st.button(f"🔄 重新生成此页", key=f"regenerate_{slide.index}", use_container_width=True):
                    try:
                        llm_client = OpenAICompatibleLLMClient.from_env()
                        prompt = build_prompt(slide, script.target_chars, script.style, custom_style)
                        result = llm_client.generate(prompt).strip()
                        if result:
                            script.script = result
                            st.session_state["scripts_edited"] = True
                            st.session_state[f"script_edit_{slide.index}"] = result
                            st.rerun()
                    except Exception as exc:
                        st.error(f"重新生成失败：{exc}")

    save_col, info_col = st.columns([1, 3])
    with save_col:
        if st.button("✏️ 保存所有修改", use_container_width=True, type="primary"):
            modified_count = 0
            for script in st.session_state["scripts"]:
                key = f"script_edit_{script.slide_index}"
                if key in st.session_state:
                    new_text = st.session_state[key].strip()
                    if new_text and new_text != script.script:
                        script.script = new_text
                        modified_count += 1
            if modified_count > 0:
                st.session_state["scripts_edited"] = True
                st.toast(f"已保存 {modified_count} 页修改！", icon="✅")
                st.rerun()
            else:
                st.toast("没有检测到修改", icon="ℹ️")
    with info_col:
        if st.session_state.get("scripts_edited"):
            st.info("✅ 当前讲稿已使用编辑后的版本，生成视频时将优先使用编辑内容。")

    download_cols = st.columns(5)
    with download_cols[0]:
        st.download_button(
            "下载 slides.json", data=to_json_bytes(slides),
            file_name="slides.json", mime="application/json",
        )
    with download_cols[1]:
        st.download_button(
            "下载 scripts.json（原始）", data=to_json_bytes(scripts),
            file_name="scripts.json", mime="application/json",
        )
    if st.session_state.get("scripts_edited"):
        with download_cols[2]:
            st.download_button(
                "下载 scripts_edited.json（编辑后）", data=to_json_bytes(scripts),
                file_name="scripts_edited.json", mime="application/json",
            )

    audio_paths = st.session_state.get("audio_paths", [])
    if audio_paths:
        with download_cols[3]:
            st.download_button(
                "下载 audio.zip",
                data=build_audio_zip_bytes([Path(p) for p in audio_paths]),
                file_name="audio.zip",
                mime="application/zip",
            )

    image_paths = st.session_state.get("image_paths", [])
    final_video_path = st.session_state.get("final_video_path")

    if image_paths:
        with download_cols[4]:
            st.download_button(
                "下载 images.zip",
                data=build_file_zip_bytes([Path(p) for p in image_paths]),
                file_name="images.zip",
                mime="application/zip",
            )

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
        video_dl_col, _ = st.columns([1, 3])
        with video_dl_col:
            st.download_button(
                "下载 final.mp4", data=video_bytes,
                file_name="final.mp4", mime="video/mp4",
            )


if __name__ == "__main__":
    main()



