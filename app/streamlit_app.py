from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from app.llm_client import OpenAICompatibleLLMClient
from app.ppt_parser import parse_pptx
from app.script_generator import STYLE_OPTIONS, generate_scripts
from app.storage import to_json_bytes


STYLE_LABELS = {
    "course": "课程讲解风格",
    "project_report": "项目汇报风格",
    "interview": "面试讲解风格",
    "sales_pitch": "销售路演风格",
}


def _save_uploaded_file(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return Path(temp_file.name)


def main() -> None:
    st.set_page_config(page_title="AI PPT 演讲稿生成器", layout="wide")
    st.title("AI PPT 演讲稿生成器")

    uploaded_file = st.file_uploader("上传 PPT 文件", type=["pptx"])
    total_minutes = st.number_input("目标总时长（分钟）", min_value=1, value=30, step=1)
    style_key = st.selectbox(
        "讲稿风格",
        options=list(STYLE_OPTIONS.keys()),
        format_func=lambda key: STYLE_LABELS[key],
    )
    custom_style = st.text_area(
        "自定义风格补充说明（可选）",
        help="例如：用通俗、稳重、适合零基础学员的方式讲解。",
    )

    if uploaded_file is None:
        st.info("请先上传一个 .pptx 文件。")
        return

    if st.button("生成讲稿", type="primary"):
        try:
            pptx_path = _save_uploaded_file(uploaded_file)
            with st.spinner("正在解析 PPT..."):
                slides = parse_pptx(pptx_path)

            st.success(f"已解析 {len(slides)} 页可读取内容。")

            with st.spinner("正在调用 LLM 生成讲稿..."):
                llm_client = OpenAICompatibleLLMClient.from_env()
                scripts = generate_scripts(
                    slides=slides,
                    total_minutes=int(total_minutes),
                    style_key=style_key,
                    custom_style=custom_style,
                    llm_client=llm_client,
                )

            st.session_state["slides"] = slides
            st.session_state["scripts"] = scripts
        except Exception as exc:
            st.error(str(exc))

    slides = st.session_state.get("slides", [])
    scripts = st.session_state.get("scripts", [])
    if not slides or not scripts:
        return

    st.subheader("生成结果")
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

    st.download_button(
        "下载 slides.json",
        data=to_json_bytes(slides),
        file_name="slides.json",
        mime="application/json",
    )
    st.download_button(
        "下载 scripts.json",
        data=to_json_bytes(scripts),
        file_name="scripts.json",
        mime="application/json",
    )


if __name__ == "__main__":
    main()
