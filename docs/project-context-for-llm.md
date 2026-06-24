# 大模型项目上下文说明

这份文档用于让新的大模型、AI 编程助手或接手开发者快速了解本项目。阅读顺序建议：先读本文件，再读 `README.md`、`docs/releases/1.0.md`，最后按需读具体代码。

## 一句话概括

这是一个本地运行的 AI PPT 演讲视频生成器：用户上传 `.pptx`，系统解析每页内容，调用 LLM 生成逐页讲稿，使用 TTS 生成语音，导出 PPT 页面图片，最后用 ffmpeg 合成 MP4 视频。

## 当前版本状态

- 当前封版版本：`1.0.0`
- Git 标签：`v1.0.0`
- 当前主要分支：`feature/streamlit-script-mvp`
- 本地入口：Streamlit 页面
- 本地地址：`http://127.0.0.1:8501`
- 验证命令：`pytest -q`
- 最近封版验证：`30 passed`

## 目标用户和项目背景

项目用于学习和求职展示。用户有 C# WinForms 基础，正在学习 Python 和 AI 应用开发。代码和文档应尽量清晰、渐进、适合解释给面试官听。

实现优先级不是追求复杂架构，而是先打通一个能运行、能展示、能解释的本地 AI 应用闭环。

## 1.0 已实现功能

- Streamlit 网页上传 `.pptx`
- 使用 `python-pptx` 解析每页标题和文本
- 根据总时长、页数和风格生成逐页讲稿
- 使用 OpenAI 兼容接口调用 LLM
- 支持 Edge TTS、MiniMax TTS、Windows 本机语音
- 页面语音引擎下拉框当前隐藏火山引擎
- 使用 PowerPoint COM 将 PPT 页面导出为 PNG
- 使用 ffmpeg 合成单页视频并拼接最终 MP4
- 调试模式默认只跑前 1 页，方便快速验证
- 项目级 Streamlit 浅色主题配置
- 基础 LangGraph Agent 编排骨架

## 暂不包含

- 云端账号系统
- 在线协作
- 数字人形象
- 模板市场
- 生产级任务队列
- 云端部署
- 完整字幕烧录流程

## 技术栈

- Python：主开发语言
- Streamlit：本地 Web UI
- python-pptx：PPT 文本解析
- OpenAI Python SDK：调用 OpenAI 兼容 LLM API
- python-dotenv：读取 `.env`
- edge-tts：免费 Edge 在线语音
- httpx：调用 MiniMax 等 HTTP API
- PowerPoint COM：Windows 本机导出 PPT 页面图片
- ffmpeg：音视频合成
- pytest：自动化测试
- LangGraph：基础流程编排

## 运行方式

安装依赖：

```powershell
pip install -r requirements.txt
```

复制配置：

```powershell
Copy-Item .env.example .env
```

在 `.env` 中填写 LLM 配置：

```text
LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL=...
```

启动：

```powershell
streamlit run app/streamlit_app.py
```

打开：

```text
http://127.0.0.1:8501
```

测试：

```powershell
pytest -q
```

## 核心执行流程

主入口是 `app/streamlit_app.py` 的 `main()`。

用户操作流程：

1. 用户上传 PPT 文件
2. `parse_pptx()` 解析 PPT，得到 `SlideContent`
3. `generate_scripts()` 为每页生成 `SlideScript`
4. `create_tts_client()` 根据页面选择创建 TTS 客户端
5. `generate_audio_files()` 逐页生成音频
6. `export_slides_to_images()` 将 PPT 页面导出成图片
7. `compose_slide_to_clip()` 合成每页视频片段
8. `concat_clips()` 拼接最终 `final.mp4`
9. Streamlit 页面展示讲稿、图片预览和最终视频下载

## 关键文件说明

- `app/streamlit_app.py`：Streamlit 页面入口，串起完整业务流程
- `app/models.py`：核心数据结构，包含 `SlideContent` 和 `SlideScript`
- `app/ppt_parser.py`：解析 `.pptx` 中的标题和文本
- `app/script_generator.py`：生成讲稿，包括风格选项、目标字数计算和 prompt 构造
- `app/llm_client.py`：OpenAI 兼容 LLM 客户端，从 `.env` 读取配置
- `app/tts_client.py`：TTS 抽象和具体实现，包括 Edge、Windows、Azure、MiniMax、火山
- `app/ppt_exporter.py`：通过 PowerPoint COM 导出页面图片
- `app/video_composer.py`：调用 ffmpeg 合成和拼接视频
- `app/ppt_agent.py`：LangGraph Agent 化流程骨架
- `app/storage.py`：JSON 序列化和保存
- `app/audio_storage.py`：音频 zip 打包工具
- `.streamlit/config.toml`：项目级 Streamlit 配置，当前为浅色主题
- `docs/releases/1.0.md`：1.0 版本说明
- `task_plan.md`：开发阶段计划和决策记录

## 三个最应该先理解的函数

1. `main()` in `app/streamlit_app.py`

   这是用户请求入口，也是当前最完整的业务流程。理解它就能理解项目如何从上传 PPT 走到最终视频。

2. `generate_scripts()` in `app/script_generator.py`

   这是 AI 应用的核心业务逻辑之一。它把 PPT 文本、目标时长和风格转换成逐页讲稿。

3. `generate_audio_files()` in `app/tts_client.py`

   这是语音生成的统一入口。不同 TTS 服务都通过相同协议接入，后续扩展新语音服务应优先复用这个接口。

## 环境变量

主要配置在 `.env.example`。

LLM：

- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

MiniMax：

- `MINIMAX_API_KEY`
- `MINIMAX_GROUP_ID`
- `MINIMAX_API_BASE_URL`

Azure 和火山相关配置保留在代码和示例中，但当前页面入口不展示火山引擎。

## 当前 UI 选择

当前页面语音引擎显示：

- Edge 免费在线语音（MP3）
- MiniMax 在线语音（自然，WAV）
- Windows 本机语音（稳定，WAV）

火山引擎底层代码仍保留，但 `TTS_ENGINE_LABELS` 中已隐藏，页面不会显示。

## 平台依赖和注意事项

- PPT 图片导出依赖 Windows + PowerPoint COM，非 Windows 或未安装 PowerPoint 时会失败
- 视频合成依赖 ffmpeg，`video_composer.py` 会尝试从系统 PATH 或 `imageio_ffmpeg` 获取
- Edge TTS 依赖网络，可能受网络波动影响
- MiniMax TTS 需要有效 API Key 和 Group ID
- `.env` 不应提交到 Git
- `output/`、`temp/`、音视频产物不应提交到 Git

## 测试覆盖

主要测试文件：

- `tests/test_ppt_parser.py`
- `tests/test_script_generator.py`
- `tests/test_llm_client.py`
- `tests/test_tts_client.py`
- `tests/test_streamlit_app.py`
- `tests/test_streamlit_entrypoint.py`
- `tests/test_ppt_exporter.py`
- `tests/test_video_composer.py`
- `tests/test_ppt_agent.py`

修改功能后优先运行：

```powershell
pytest -q
```

## 给后续大模型的开发建议

- 先读 `app/streamlit_app.py`，不要直接改底层模块
- 先跑 `pytest -q`，确认基线是绿的
- 做小步修改，每次只改一个明确行为
- 不要把 `.env`、`output/`、`temp/`、mp4、mp3、wav 提交进 Git
- 新增语音引擎时，优先实现 `TTSClientProtocol`
- 修改页面语音选项时，同步更新 `tests/test_streamlit_app.py`
- 修改入口导入方式时，同步关注 `tests/test_streamlit_entrypoint.py`
- 不要大规模重写；这个项目当前目标是学习、展示和可解释

## 适合面试表达的项目总结

这个项目是一个本地 AI 应用闭环：我用 Python 和 Streamlit 做了一个 PPT 演讲视频生成器。用户上传 PPT 后，系统会解析每页文本，调用大模型生成逐页讲稿，再用 TTS 生成语音，通过 PowerPoint 导出页面图片，最后调用 ffmpeg 合成 MP4 视频。项目中我抽象了 LLM 和 TTS 接口，支持替换不同模型和语音服务，并用 pytest 覆盖了核心流程。这个项目展示了我从 C# 桌面开发转向 AI 应用开发时，对文件处理、API 调用、音视频处理和工程化测试的综合实践。
