# Streamlit 讲稿生成 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建第一个可运行 MVP：用户在 Streamlit 上传 `.pptx`，系统解析每页文本，调用 OpenAI 兼容 LLM 生成逐页讲稿，并支持页面预览和 JSON 下载。

**Architecture:** 使用本地 Python 流水线，Streamlit 只负责页面交互；PPT 解析、讲稿生成、LLM 调用、JSON 导出分别放在独立模块。LLM 调用通过 OpenAI 兼容接口封装，后续可替换 DeepSeek、OpenAI、通义、智谱或 Kimi。

**Tech Stack:** Python 3.10+、Streamlit、python-pptx、openai Python SDK、python-dotenv、pytest。

## Global Constraints

- 第一版入口为 Streamlit 网页版。
- 第一版只实现：PPT 解析、真实 LLM 讲稿生成、页面预览、下载 `slides.json` 和 `scripts.json`。
- 第一版不实现：TTS、MP4 合成、数字人、用户账号、云端部署、LangGraph 编排。
- LLM 接入必须使用 OpenAI 兼容配置，不能把 DeepSeek 写死在业务逻辑里。
- 讲稿风格必须支持内置选项和自定义补充说明。
- 测试不能依赖真实 API Key，LLM 调用必须 mock。

---

## File Structure

```text
app/
  __init__.py
  streamlit_app.py
  ppt_parser.py
  script_generator.py
  llm_client.py
  models.py
  storage.py
tests/
  __init__.py
  test_script_generator.py
  test_storage.py
.env.example
requirements.txt
README.md
docs/learning-log.md
progress.md
task_plan.md
```

## Task 1: 项目依赖和基础数据模型

**Files:**
- Create: `app/__init__.py`
- Create: `app/models.py`
- Create: `tests/__init__.py`
- Create: `requirements.txt`
- Create: `.env.example`
- Modify: `README.md`

**Interfaces:**
- Produces: `SlideContent(index: int, title: str, body: str, raw_text: str)` dataclass
- Produces: `SlideScript(slide_index: int, title: str, script: str, target_chars: int, style: str)` dataclass
- Later tasks import these models from `app.models`

- [ ] **Step 1: 创建基础依赖文件**

Create `requirements.txt`:

```text
streamlit>=1.36.0
python-pptx>=0.6.23
openai>=1.40.0
python-dotenv>=1.0.1
pytest>=8.2.0
```

Create `.env.example`:

```text
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
```

- [ ] **Step 2: 创建 Python 包入口**

Create `app/__init__.py`:

```python
"""AI PPT video agent MVP package."""
```

Create `tests/__init__.py`:

```python
"""Tests for the AI PPT video agent MVP."""
```

- [ ] **Step 3: 创建数据模型**

Create `app/models.py`:

```python
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SlideContent:
    index: int
    title: str
    body: str
    raw_text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SlideScript:
    slide_index: int
    title: str
    script: str
    target_chars: int
    style: str

    def to_dict(self) -> dict:
        return asdict(self)
```

- [ ] **Step 4: 更新 README 的运行说明**

Modify `README.md` and add:

```markdown
## 本地运行

1. 创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. 复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

3. 在 `.env` 中填写你的 LLM 配置。

4. 启动 Streamlit：

```powershell
streamlit run app/streamlit_app.py
```
```

- [ ] **Step 5: 验证依赖可安装**

Run:

```powershell
python -m pip install -r requirements.txt
```

Expected: command exits with code 0.

- [ ] **Step 6: Commit**

```powershell
git add app/__init__.py app/models.py tests/__init__.py requirements.txt .env.example README.md
git commit -m "chore: add python project foundation"
```

## Task 2: JSON 存储和下载数据

**Files:**
- Create: `app/storage.py`
- Create: `tests/test_storage.py`

**Interfaces:**
- Consumes: `SlideContent`, `SlideScript`
- Produces: `to_json_bytes(items: Sequence[Any]) -> bytes`
- Produces: `save_json(path: Path, items: Sequence[Any]) -> None`

- [ ] **Step 1: 写失败测试**

Create `tests/test_storage.py`:

```python
from pathlib import Path

from app.models import SlideContent, SlideScript
from app.storage import save_json, to_json_bytes


def test_to_json_bytes_serializes_dataclasses_as_utf8_json():
    slides = [
        SlideContent(index=1, title="标题", body="正文", raw_text="标题\n正文"),
    ]

    payload = to_json_bytes(slides)

    assert b"\\xe6\\xa0\\x87\\xe9\\xa2\\x98" in payload
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
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
pytest tests/test_storage.py -v
```

Expected: FAIL because `app.storage` does not exist.

- [ ] **Step 3: 实现 storage 模块**

Create `app/storage.py`:

```python
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Sequence


def _to_plain_object(item: Any) -> Any:
    if is_dataclass(item):
        return asdict(item)
    if hasattr(item, "to_dict"):
        return item.to_dict()
    return item


def to_json_bytes(items: Sequence[Any]) -> bytes:
    plain_items = [_to_plain_object(item) for item in items]
    text = json.dumps(plain_items, ensure_ascii=False, indent=2)
    return text.encode("utf-8")


def save_json(path: Path, items: Sequence[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_json_bytes(items))
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
pytest tests/test_storage.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```powershell
git add app/storage.py tests/test_storage.py
git commit -m "feat: add json storage helpers"
```

## Task 3: 讲稿生成逻辑和提示词构建

**Files:**
- Create: `app/script_generator.py`
- Create: `tests/test_script_generator.py`

**Interfaces:**
- Consumes: `SlideContent`, `SlideScript`
- Produces: `STYLE_OPTIONS: dict[str, str]`
- Produces: `calculate_target_chars(total_minutes: int, slide_count: int, chars_per_minute: int = 220) -> int`
- Produces: `build_prompt(slide: SlideContent, target_chars: int, style_key: str, custom_style: str = "") -> str`
- Produces: `generate_scripts(slides: Sequence[SlideContent], total_minutes: int, style_key: str, custom_style: str, llm_client: LLMClientProtocol) -> list[SlideScript]`

- [ ] **Step 1: 写失败测试**

Create `tests/test_script_generator.py`:

```python
from app.models import SlideContent
from app.script_generator import build_prompt, calculate_target_chars, generate_scripts


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        assert "第一页标题" in prompt
        return "这是一段由测试客户端返回的讲稿。"


def test_calculate_target_chars_uses_total_minutes_and_slide_count():
    assert calculate_target_chars(total_minutes=120, slide_count=60) == 440


def test_calculate_target_chars_never_returns_zero():
    assert calculate_target_chars(total_minutes=1, slide_count=60) == 10


def test_build_prompt_contains_style_slide_text_and_target_length():
    slide = SlideContent(
        index=1,
        title="第一页标题",
        body="第一页正文",
        raw_text="第一页标题\n第一页正文",
    )

    prompt = build_prompt(
        slide=slide,
        target_chars=440,
        style_key="course",
        custom_style="适合零基础学员。",
    )

    assert "课程讲解风格" in prompt
    assert "适合零基础学员" in prompt
    assert "第一页标题" in prompt
    assert "第一页正文" in prompt
    assert "440" in prompt


def test_generate_scripts_calls_llm_and_returns_slide_scripts():
    slides = [
        SlideContent(
            index=1,
            title="第一页标题",
            body="第一页正文",
            raw_text="第一页标题\n第一页正文",
        )
    ]

    scripts = generate_scripts(
        slides=slides,
        total_minutes=2,
        style_key="course",
        custom_style="",
        llm_client=FakeLLMClient(),
    )

    assert len(scripts) == 1
    assert scripts[0].slide_index == 1
    assert scripts[0].script == "这是一段由测试客户端返回的讲稿。"
    assert scripts[0].style == "course"
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
pytest tests/test_script_generator.py -v
```

Expected: FAIL because `app.script_generator` does not exist.

- [ ] **Step 3: 实现 script_generator 模块**

Create `app/script_generator.py`:

```python
from __future__ import annotations

from typing import Protocol, Sequence

from app.models import SlideContent, SlideScript


class LLMClientProtocol(Protocol):
    def generate(self, prompt: str) -> str:
        ...


STYLE_OPTIONS: dict[str, str] = {
    "course": "课程讲解风格：表达清楚、耐心，适合培训和教学。",
    "project_report": "项目汇报风格：结构化、专业，适合作品展示和进度汇报。",
    "interview": "面试讲解风格：突出技术决策、个人负责内容和项目亮点。",
    "sales_pitch": "销售路演风格：更有说服力，适合产品介绍。",
}


def calculate_target_chars(
    total_minutes: int,
    slide_count: int,
    chars_per_minute: int = 220,
) -> int:
    if total_minutes <= 0:
        raise ValueError("目标总时长必须大于 0 分钟。")
    if slide_count <= 0:
        raise ValueError("PPT 至少需要 1 页。")
    return max(10, round(total_minutes * chars_per_minute / slide_count))


def build_prompt(
    slide: SlideContent,
    target_chars: int,
    style_key: str,
    custom_style: str = "",
) -> str:
    style = STYLE_OPTIONS.get(style_key)
    if style is None:
        raise ValueError(f"未知讲稿风格：{style_key}")

    custom_line = ""
    if custom_style.strip():
        custom_line = f"\n用户补充风格要求：{custom_style.strip()}"

    return f"""你是一名专业中文演讲稿作者。请根据下面 PPT 页面内容，生成这一页的中文演讲稿。

讲稿风格：{style}{custom_line}
目标长度：约 {target_chars} 个中文字符。

要求：
1. 不要照读 PPT 原文，要补充解释和自然过渡。
2. 只输出演讲稿正文，不要输出标题、编号或 Markdown。
3. 内容要围绕这一页，不要虚构 PPT 中没有依据的具体数据。

PPT 页码：第 {slide.index} 页
PPT 标题：{slide.title or "无标题"}
PPT 内容：
{slide.raw_text}
"""


def generate_scripts(
    slides: Sequence[SlideContent],
    total_minutes: int,
    style_key: str,
    custom_style: str,
    llm_client: LLMClientProtocol,
) -> list[SlideScript]:
    if not slides:
        raise ValueError("没有可生成讲稿的 PPT 页面。")

    target_chars = calculate_target_chars(total_minutes, len(slides))
    results: list[SlideScript] = []

    for slide in slides:
        prompt = build_prompt(slide, target_chars, style_key, custom_style)
        script = llm_client.generate(prompt).strip()
        if not script:
            raise ValueError(f"第 {slide.index} 页 LLM 返回空内容。")
        results.append(
            SlideScript(
                slide_index=slide.index,
                title=slide.title,
                script=script,
                target_chars=target_chars,
                style=style_key,
            )
        )

    return results
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
pytest tests/test_script_generator.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```powershell
git add app/script_generator.py tests/test_script_generator.py
git commit -m "feat: add slide script generation logic"
```

## Task 4: PPT 解析和 LLM 客户端

**Files:**
- Create: `app/ppt_parser.py`
- Create: `app/llm_client.py`

**Interfaces:**
- Produces: `parse_pptx(file: BinaryIO | str | Path) -> list[SlideContent]`
- Produces: `OpenAICompatibleLLMClient.from_env() -> OpenAICompatibleLLMClient`
- Produces: `OpenAICompatibleLLMClient.generate(prompt: str) -> str`

- [ ] **Step 1: 实现 PPT 解析模块**

Create `app/ppt_parser.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from pptx import Presentation

from app.models import SlideContent


def _shape_text(shape) -> str:
    if not hasattr(shape, "text"):
        return ""
    return str(shape.text).strip()


def parse_pptx(file: BinaryIO | str | Path) -> list[SlideContent]:
    presentation = Presentation(file)
    slides: list[SlideContent] = []

    for zero_based_index, slide in enumerate(presentation.slides):
        text_parts: list[str] = []
        title = ""

        if slide.shapes.title is not None:
            title = _shape_text(slide.shapes.title)
            if title:
                text_parts.append(title)

        for shape in slide.shapes:
            text = _shape_text(shape)
            if not text:
                continue
            if text == title:
                continue
            text_parts.append(text)

        raw_text = "\n".join(text_parts).strip()
        body = "\n".join(part for part in text_parts if part != title).strip()
        slides.append(
            SlideContent(
                index=zero_based_index + 1,
                title=title,
                body=body,
                raw_text=raw_text,
            )
        )

    readable_slides = [slide for slide in slides if slide.raw_text]
    if not readable_slides:
        raise ValueError("PPT 中没有可提取的文本。")
    return readable_slides
```

- [ ] **Step 2: 实现 OpenAI 兼容 LLM 客户端**

Create `app/llm_client.py`:

```python
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str


class OpenAICompatibleLLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    @classmethod
    def from_env(cls) -> "OpenAICompatibleLLMClient":
        load_dotenv()
        base_url = os.getenv("LLM_BASE_URL", "").strip()
        api_key = os.getenv("LLM_API_KEY", "").strip()
        model = os.getenv("LLM_MODEL", "").strip()

        missing = [
            name
            for name, value in {
                "LLM_BASE_URL": base_url,
                "LLM_API_KEY": api_key,
                "LLM_MODEL": model,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"缺少 LLM 环境变量：{', '.join(missing)}")

        return cls(LLMConfig(base_url=base_url, api_key=api_key, model=model))

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的中文 PPT 演讲稿生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if content is None or not content.strip():
            raise ValueError("LLM 返回空内容。")
        return content.strip()
```

- [ ] **Step 3: 手动语法检查**

Run:

```powershell
python -m compileall app
```

Expected: command exits with code 0.

- [ ] **Step 4: 运行已有测试**

Run:

```powershell
pytest -v
```

Expected: all existing tests pass.

- [ ] **Step 5: Commit**

```powershell
git add app/ppt_parser.py app/llm_client.py
git commit -m "feat: add ppt parser and llm client"
```

## Task 5: Streamlit 页面和端到端手动验证

**Files:**
- Create: `app/streamlit_app.py`
- Modify: `README.md`
- Modify: `docs/learning-log.md`
- Modify: `progress.md`
- Modify: `task_plan.md`

**Interfaces:**
- Consumes: `parse_pptx`
- Consumes: `OpenAICompatibleLLMClient.from_env`
- Consumes: `generate_scripts`
- Consumes: `to_json_bytes`
- Produces: Streamlit UI with PPT upload, duration input, style select, custom style input, generated result preview, and JSON download buttons

- [ ] **Step 1: 创建 Streamlit 页面**

Create `app/streamlit_app.py`:

```python
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
        with st.expander(f"第 {slide.index} 页：{slide.title or '无标题'}", expanded=False):
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
```

- [ ] **Step 2: 运行语法检查和测试**

Run:

```powershell
python -m compileall app
pytest -v
```

Expected: compileall exits with code 0, pytest passes.

- [ ] **Step 3: 启动 Streamlit 手动检查**

Run:

```powershell
streamlit run app/streamlit_app.py
```

Expected:

- Browser shows `AI PPT 演讲稿生成器`.
- Page has PPT upload, duration input, style dropdown, custom style text area, and generate button.
- Without `.env`, clicking generation after upload shows a missing environment variable error.

- [ ] **Step 4: 用真实 API Key 手动验证**

Create local `.env` from `.env.example`, fill values:

```text
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your_real_api_key
LLM_MODEL=deepseek-chat
```

Run:

```powershell
streamlit run app/streamlit_app.py
```

Expected:

- Uploading a `.pptx` extracts slide text.
- Clicking `生成讲稿` calls the LLM.
- Page shows slide source text and generated script.
- Download buttons produce valid JSON files.

- [ ] **Step 5: 更新学习记录和计划状态**

Append to `docs/learning-log.md`:

```markdown
## 2026-06-23 Streamlit MVP 实现

### 已完成

- 搭建 Streamlit 页面入口。
- 实现 PPT 文本解析。
- 实现 OpenAI 兼容 LLM 调用。
- 实现逐页讲稿生成和 JSON 下载。

### 学到的内容

- Streamlit 适合快速验证 AI 应用交互。
- LLM 调用应和页面逻辑分离，方便后续换模型或改成 Agent 工具。
- 测试中不能依赖真实 API Key，要用 mock 或 fake client。
```

Update `task_plan.md` Phase 1、Phase 2、Phase 3 status to `complete` for this MVP, and note that Phase 4-7 remain future work.

Append to `progress.md`:

```markdown
- 已完成 Streamlit 讲稿生成 MVP 的本地实现和验证。
```

- [ ] **Step 6: Commit and push**

```powershell
git add app/streamlit_app.py README.md docs/learning-log.md progress.md task_plan.md
git commit -m "feat: add streamlit script generation mvp"
git push
```

## Final Verification

Run before declaring the MVP complete:

```powershell
python -m compileall app
pytest -v
git status --short --branch
```

Expected:

- `compileall` exits with code 0.
- `pytest` passes.
- `git status --short --branch` shows local `main` tracking `origin/main` with no uncommitted files after the final push.

## Self-Review

- Spec coverage: PPT upload, duration input, style selection, custom style, text extraction, OpenAI-compatible LLM call, preview, JSON downloads, and deterministic tests are covered.
- Scope check: TTS, video rendering, digital avatar, cloud deployment, and LangGraph remain outside this MVP.
- Type consistency: later tasks consume `SlideContent`, `SlideScript`, `parse_pptx`, `generate_scripts`, `OpenAICompatibleLLMClient`, and `to_json_bytes` exactly as defined in earlier tasks.
