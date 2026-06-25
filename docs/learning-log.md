# 学习日志

## 2026-06-23

### 今天的目标

开始设计一个“AI PPT 演讲视频生成器”，并准备把项目和学习过程同步到 GitHub。

### 已理解的核心思路

- 这个项目不是简单的 PPT 转视频，而是一条流水线：
  `PPT -> 解析内容 -> 生成讲稿 -> 生成语音 -> 导出画面 -> 合成视频`
- 第一版不要直接做数字人，先打通“PPT + 讲稿 + 配音 + MP4”的最小闭环。
- Agent 不应该直接生成视频，而应该负责规划流程、调用工具、检查结果。
- 更稳的路线是先写普通 Python 流水线，再用 LangGraph 包装成 Agent。

### 当前技术选择

- 核心语言：Python
- 后续界面：可选 C# WinForms/WPF
- PPT 解析：python-pptx
- 视频合成：ffmpeg
- Agent 框架：LangGraph

### 下一步

- 初始化项目结构
- 写第一个功能：读取 PPT 并提取每页文本
- 学习如何把本地项目提交到 GitHub

## 2026-06-23 Streamlit MVP 实现

### 已完成

- 搭建 Streamlit 页面入口。
- 实现 PPT 文本解析。
- 实现 OpenAI 兼容 LLM 调用。
- 实现逐页讲稿生成和 JSON 下载。

### 学到的内容

- Streamlit 适合快速验证 AI 应用交互。
- LLM 调用应和页面逻辑分离，方便后续换模型或改成 Agent 工具。
- 测试中不能依赖真实 API Key，要用 fake client 或环境变量隔离。

## 2026-06-23 语音生成功能

### 已完成

- 增加 `edge-tts` 依赖。
- 增加逐页音频生成模块。
- 增加音频 ZIP 打包下载模块。
- 在 Streamlit 页面增加语音选择、生成语音和下载 `audio.zip` 功能。
- 增加 Windows 本机中文语音作为默认稳定方案。

### 注意事项

- 单元测试不调用真实 TTS 服务，只验证调度和打包逻辑。
- 当前环境下 edge-tts 真实调用存在 `NoAudioReceived` 不稳定情况，所以默认使用 Windows 本机语音生成 WAV。后续如果需要更自然的声音，应考虑切换到 Azure Speech、OpenAI TTS 或其他正式 TTS API。

## 2026-06-23 PPT 页面导出图片 (Phase 5)

### 已完成

- 创建 \pp/ppt_exporter.py\：通过 PowerPoint COM 将 PPT 逐页导出为 PNG 图片。
- 后台运行 \powerpoint.Visible = False\（默认即为隐藏，删除该赋值避免 COM 权限错误）。
- 导出图片质量优化：尝试注册表设置 \ExportBitmapResolution=192\（对应 1920x1080）。
- 容错处理：关闭 presentation 和 powerpoint 放在 \inally\ 块中，确保资源释放。
- 测试：mock win32com 模块验证调度逻辑（注意两层模块的 mock 方法）。
- Streamlit 集成：页面底部增加"导出页面图片"区域，按钮触发导出后逐页预览。

### 学到的内容

- \win32com.client.Dispatch("PowerPoint.Application")\ 是 Windows 上调用 Office 的标准方式。
- PowerPoint COM 对象默认隐藏，设置 \Visible = False\ 在某些环境会抛 COM 权限错误，直接去掉即可。
- 测试中 mock win32com 必须同时设置 \sys.modules["win32com"]\ 和 \sys.modules["win32com.client"]\，且让父 mock 的 \.client\ 属性指向子 mock，否则 import 链路不对。
- MagicMock 的链式属性调用（\mock_app.Presentations.Open(...)\）容易踩坑：中间属性在连续访问中可能创建不同子 mock。最佳实践是直接替换中间属性为独立 MagicMock 实例。
## 2026-06-25 PPT 生成功能暂停

### 决策
经验证，AI 直接生成 PPT 的内容质量不够好（LLM 输出通用模板，缺乏行业深度），python-pptx 构建的视觉效果也不够专业。决定暂时屏蔽此功能，回归视频流水线的质量优化。

### 代码变动
- 移除 `/` in streamlit_app.py → 移除了"生成新 PPT"UI 区域、清理了无用 import、删除了 3 个不再调用的 helper 函数
- PPT 生成模块文件（`ppt_outline_generator.py`、`ppt_content_generator.py`、`ppt_builder.py`、`ppt_template_analyzer.py`）保留在 `app/` 目录中，代码不删除
- 测试数：53 → 55

### 学到的内容
- DeepSeek 的 `response_format={"type": "json_object"}` 会让模型忽略 user prompt 只听从 system prompt，导致主题偏离。修复方式：去掉 JSON mode，把关键信息嵌入 system prompt
- PowerShell 管道 `@'...'@ | python` 会破坏中文字符。修复方式：先写文件再执行
- Streamlit 的 `st.expander` 不能嵌套

## 2026-06-25 版本发布习惯

### 决策

后续每完成一个明确版本，都要保存成独立版本分支，并推送到 GitHub。

### 固定动作

- 完成功能后先运行测试和必要的手动验证。
- 更新 `README.md`、`docs/project-context-for-llm.md`、对应路线图文档和运行说明。
- 更新 `docs/learning-log.md`，记录本版本完成内容、问题、解决方案和面试表达。
- 更新 `progress.md`，记录版本号、分支名、测试结果和 GitHub 推送状态。
- 创建 `version/x.y-feature-name` 分支。
- 提交代码和文档。
- 推送到 GitHub。
- 必要时打 `vX.Y.Z` 标签。

### 学到的内容

版本管理不只是代码提交。对学习型项目来说，每个版本都应该留下三类记录：

- 代码记录：分支、提交、标签
- 项目记录：README、上下文文档、路线图
- 成长记录：学习日志、问题复盘、面试表达

这样项目不仅能运行，也能展示持续迭代的过程。

## 2026-06-25 Version 1.1 讲稿可编辑版本完成
### 已完成
- 讲稿预览区改为可编辑文本框
- 编辑后讲稿用于 TTS 和视频合成
- 下载 scripts.json（原始）+ scripts_edited.json（编辑后）
- 单页讲稿重新生成按钮（不影响其他页）
- chars_per_minute 200→230 修复时长偏移
- 视频生成后显示实际时长对比
- 视频画质提升（CRF 18 + 300 DPI 导出）
- 男声默认排第一
- Edge TTS 重试延迟 + 友好错误提示
- pytest 55 passed

### 学到的内容
- Streamlit 的 session_state 用于追踪编辑状态和跨重绘保持数据
- ffmpeg CRF 参数控制编码质量，对幻灯片画面 CRF 18 效果显著
- 中文路径会导致 ONNX Runtime 加载模型失败（system error 13）
- espeak-ng 中文语音数据缺失时 phonemizer 会报错
- hf-mirror.com 可作为 HuggingFace 国内镜像
- uv 管理 Python 依赖比 pip 更严格（TOML 格式要求严格）
- 302 重定向的 Content-Length 可能为 0，需 follow redirect

### 面试可以这样表达
> 讲稿可编辑这个版本，我没有把 LLM 的输出直接当成最终结果，而是设计了一个可编辑的中间层。用户可以逐页检查、修改和重新生成讲稿，这样可以人工修正 LLM 的偏差，等确认无误后再进入语音和视频合成。这体现了我对 AI 应用可控性和人机协作流程的理解。
