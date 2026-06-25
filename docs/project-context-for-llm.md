# 大模型项目上下文说明

这份文档用于让新的大模型、AI 编程助手或接手开发者快速了解本项目。阅读顺序建议：先读本文件，再读 `README.md`、`docs/releases/1.0.md`、`docs/run-guide.md`，最后按需读具体代码。

## 一句话概括

这是一个本地运行的 AI 演讲视频生成器：用户上传 `.pptx`，系统解析每页内容，调用 LLM 生成逐页讲稿，使用 TTS 生成语音，导出 PPT 页面图片，最后用 ffmpeg 合成 MP4 视频。

## 当前版本状态

- 当前版本：`1.1.0`（PPT 生成功能已暂停，回归视频流水线优化）
- Git 标签：`v1.1.0`（1.1 封版）
- 当前主要分支：`feature/streamlit-script-mvp`
- 本地入口：Streamlit 页面
- 本地地址：`http://127.0.0.1:8501`
- 启动方式：`streamlit run app/streamlit_app.py --server.headless true`
- 验证命令：`pytest -q`（55 passed）
- 项目文件数：`app/` 下 16 个 `.py`，`tests/` 下 16 个 `.py`

## 目标用户和项目背景

项目用于学习和求职展示。用户有 C# WinForms 基础，正在学习 Python 和 AI 应用开发。代码和文档应尽量清晰、渐进、适合解释给面试官听。

实现优先级不是追求复杂架构，而是先打通一个能运行、能展示、能解释的本地 AI 应用闭环。

## 1.1 已实现功能（视频生成流水线 + 讲稿编辑）

- Streamlit 网页上传 `.pptx`
- 使用 `python-pptx` 解析每页标题和文本
- 根据总时长、页数和风格生成逐页讲稿
- 使用 OpenAI 兼容接口调用 LLM
- 支持 Edge TTS、MiniMax TTS、Windows 本机语音
- 使用 PowerPoint COM 将 PPT 页面导出为 PNG
- 使用 ffmpeg 合成单页视频并拼接最终 MP4
- 调试模式默认只跑前 1 页，方便快速验证
- 项目级 Streamlit 浅色主题配置
- 基础 LangGraph Agent 编排骨架
- 逐页讲稿可编辑，支持保存和单页重新生成
- 视频时长自动对齐（chars_per_minute 230）
- 视频画质提升（CRF 18 + 300 DPI 导出）
- 视频生成后显示实际时长对比

## PPT 生成实验（已暂停）

> **状态：** 此功能已暂停。代码模块保留在 `app/` 目录中，但 Streamlit 页面入口已移除。
> 核心问题：LLM 内容质量不够好（通用模板化），python-pptx 视觉效果不够专业。
> 待解决后再重新开启。


### 模式 A：从零生成 PPT

用户填主题/用途/受众/页数/风格 → AI 出大纲 → AI 出每页内容 → python-pptx 构建 `.pptx` 文件 → 页面下载。

### 模式 B：参考 PPT 生成

用户上传参考 PPT → 解析页数/标题/正文 → 提取公司名/配色/字体等风格信息 → 结合用户新要求 → 生成新大纲 → 生成新内容 → 构建 `.pptx`（尝试匹配参考 PPT 风格）。

### 参考 PPT 风格提取（ppt_template_analyzer.py）

从参考 PPT 中提取以下信息，用于匹配新 PPT 风格：
- **公司名** — 从文档属性（`core_properties.company`）
- **主题色** — 从 slide master 的 `clrScheme` 提取配色
- **字体** — 扫描所有 text run 统计最常用的字体
- **风格描述文本** — 上述信息的汇总，传给 LLM 提示

## 技术栈

- **Python 3.10+**：主开发语言
- **Streamlit**：本地 Web UI
- **python-pptx**：PPT 解析（1.0）+ PPT 构建（1.1）
- **OpenAI Python SDK**：调用 OpenAI 兼容 LLM API（当前使用 DeepSeek）
- **python-dotenv**：读取 `.env`
- **edge-tts**：免费 Edge 在线语音
- **httpx**：调用 MiniMax 等 HTTP API
- **PowerPoint COM**：Windows 本机导出 PPT 页面图片
- **ffmpeg**：音视频合成
- **pytest**：自动化测试
- **LangGraph**：基础流程编排

## 运行方式

详见 `docs/run-guide.md`，关键命令：

```powershell
cd D:\学习\ppt
pip install -r requirements.txt          # 安装依赖
Copy-Item .env.example .env              # 复制配置
# 编辑 .env 填写 LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
streamlit run app/streamlit_app.py --server.headless true  # 启动（不开浏览器）
pytest -q                                 # 跑全部测试
```

## 核心执行流程

### 视频生成流水线（1.0）

```
上传 PPT
  → parse_pptx()         # 解析每页文本
  → generate_scripts()   # LLM 生成逐页讲稿
  → create_tts_client()  # 选择语音引擎
  → generate_audio_files() # 逐页生成音频
  → export_slides_to_images() # PowerPoint COM 导出 PNG
  → compose_slide_to_clip()  # ffmpeg 合成单页片段
  → concat_clips()       # 拼接最终 MP4
```

### PPT 生成流水线（1.1）

```
模式 A（从零）：
  用户输入（主题/场景/受众/页数）
  → generate_outline()   # LLM 生成结构化大纲（JSON）
  → generate_content()   # LLM 生成每页内容（JSON）
  → build_pptx()         # python-pptx 构建 .pptx 文件
  → 页面下载 / 继续做讲稿视频

模式 B（参考）：
  上传参考 PPT
  → analyze_reference_pptx()  # 提取结构 + 风格信息
  → generate_outline_with_reference()  # 参考风格生成新大纲
  → generate_content()   # 生成每页内容
  → build_pptx(ref_context)  # 参考风格匹配构建 .pptx
```

## 关键文件说明

### 视频流水线（1.0）
- `app/streamlit_app.py`：页面入口，`main()` 串起所有流程。原内含 PPT 生成相关 helper 函数已被移除
- `app/models.py`：数据结构，包括 `SlideContent`、`SlideScript`、`PPTGenerationInput`、`PPTOutlineItem`、`GeneratedSlideContent`、`ReferenceContext` 等
- `app/ppt_parser.py`：解析 `.pptx` 中的标题和文本
- `app/script_generator.py`：生成讲稿
- `app/llm_client.py`：OpenAI 兼容 LLM 客户端。注意 `generate_with_system()` 已去掉 `response_format`（详见已知问题）
- `app/tts_client.py`：多引擎 TTS 抽象层
- `app/ppt_exporter.py`：PowerPoint COM 导出页面图片
- `app/video_composer.py`：ffmpeg 合成/拼接视频
- `app/ppt_agent.py`：LangGraph 骨架
- `app/storage.py`：JSON 序列化
- `app/audio_storage.py`：音频 zip 打包

### PPT 生成（1.1 新增）
- `app/ppt_outline_generator.py`：LLM 生成结构化大纲（支持 `generate_outline` 和 `generate_outline_with_reference`）
- `app/ppt_content_generator.py`：LLM 生成每页具体内容（标题 + bullets + speaker_hint）
- `app/ppt_builder.py`：python-pptx 构建 `.pptx`，可选接受 `ref_context` 匹配风格
- `app/ppt_template_analyzer.py`：解析参考 PPT，提取页数/公司名/配色/字体

### 测试
- `tests/test_ppt_outline_generator.py`（7 tests）
- `tests/test_ppt_content_generator.py`（5 tests）
- `tests/test_ppt_builder.py`（6 tests）
- `tests/test_ppt_template_analyzer.py`（3 tests）

## 最适合新开发者阅读的顺序

1. `app/streamlit_app.py` 的 `main()` — 理解页面入口和完整业务流程
2. `app/ppt_parser.py` 的 `parse_pptx()` — 理解 PPT 文本解析
3. `app/script_generator.py` 的 `generate_scripts()` — 理解讲稿生成的 AI 调用
4. `app/llm_client.py` — 理解 LLM 客户端封装
5. `app/tts_client.py` 的 `generate_audio_files()` — 理解多引擎 TTS 统一入口

## 已知问题和注意事项

### 重要：DeepSeek JSON mode 导致主题偏离
`response_format={"type": "json_object"}` 会导致 DeepSeek 忽略 user prompt、完全听 system prompt，从而生成通用模板内容而非用户指定主题。
- 当前修复：去掉 `response_format`，把主题信息嵌入 system prompt，靠 prompt 本身要求 JSON 输出
- 涉及文件：`app/llm_client.py`、`app/ppt_outline_generator.py`

### 重要：PowerShell stdin 中文编码损坏
在 PowerShell 中通过 `@'"..."'@ | python` 管道传递 Python 代码时，中文字符会被替换为 `?`。这会导致 LLM 收到乱码并返回错误主题。
- 修复方案：先把 Python 脚本写入 `.py` 文件再用 `python xxx.py` 执行，不要用管道
- 涉及：本地开发习惯，不影响 `streamlit run` 方式运行

### Streamlit expander 嵌套限制
`st.expander` 不能嵌套在另一个 `st.expander` 内部，否则抛 `StreamlitAPIException`。
- 当前修复：用 `st.markdown("---")` 分隔替代内层 expander
- 涉及：`app/streamlit_app.py` 的 `_show_ppt_generation_results()`

### 其他注意事项
- PPT 图片导出依赖 Windows + PowerPoint COM
- 视频合成依赖 ffmpeg
- Edge TTS 依赖网络
- `.env` 不应提交到 Git
- `output/`、`temp/`、音视频产物不应提交到 Git
- Streamlit 启动加 `--server.headless true` 阻止自动打开浏览器

## 环境变量

主要配置在 `.env.example`。注意语言模型 API 用的是 DeepSeek（兼容 OpenAI 协议），配置文件：

- `LLM_BASE_URL=https://api.deepseek.com`
- `LLM_API_KEY=sk-...`
- `LLM_MODEL=deepseek-chat`

## 测试覆盖

全部 55 个测试通过：

```powershell
pytest -q
```

修改功能后优先运行此命令，确认基线是绿的。

## 给后续大模型的开发建议

- 先读 `docs/project-context-for-llm.md`（本文件），不要直接改代码
- 先跑 `pytest -q`，确认基线是绿的（55 passed）
- 做小步修改，每次只改一个明确行为
- 不要把 `.env`、`output/`、`temp/`、mp4、mp3、wav 提交进 Git
- 新增语音引擎时，优先实现 `TTSClientProtocol`
- 修改页面选项时，同步更新对应测试
- **不要在 PowerShell 中用管道传中文代码** — 先写文件再执行
- 不要大规模重写；这个项目当前目标是学习、展示和可解释

## 适合面试表达的项目总结

这个项目是一个本地 AI 应用闭环：我用 Python 和 Streamlit 做了一个 **AI PPT 演讲视频生成器**：用户上传 PPT 后，系统自动解析文本、调用大模型生成逐页讲稿、调用 TTS 生成语音，最后合成 MP4 演讲视频。项目中我抽象了 LLM 和 TTS 接口，用 DeepSeek 做内容生成，用 pytest 覆盖了 55 个测试。这个项目展示了我从 C# 桌面开发转向 AI 应用开发时，对 LLM 调用、结构化输出、文件处理、音视频处理和工程化测试的综合实践。

