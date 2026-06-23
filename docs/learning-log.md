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
