# AI PPT 演讲视频生成器

这是一个面向学习和求职展示的 AI 应用项目。目标是把一个本地 PPT 文件自动生成带讲稿、配音、字幕和视频合成结果的演讲视频。

## 项目目标

用户上传或选择一个 `.pptx` 文件后，系统自动完成：

1. 解析每页 PPT 内容
2. 根据目标总时长生成逐页演讲稿
3. 生成每页语音
4. 导出每页画面
5. 合成最终 MP4 视频

## 当前版本

当前封版版本：`1.0.0`

1.0 已完成本地最小闭环：上传 PPT、生成讲稿、生成语音、导出页面图片并合成 MP4 视频。版本说明见 [docs/releases/1.0.md](docs/releases/1.0.md)。

## 第一版范围

第一版优先做本地最小闭环：

- 本地读取 `.pptx`
- 生成 `slides.json`
- 生成逐页讲稿
- 支持 Edge、MiniMax、Windows 本机语音生成
- 使用 ffmpeg 合成视频
- 使用 LangGraph 做基础 Agent 编排

暂不实现：

- 数字人
- 云端账号系统
- 在线协作
- 复杂模板市场

## 技术路线

- Python：核心处理流程
- python-pptx：解析 PPT 文本
- LLM API：生成演讲稿
- TTS API：生成语音
- ffmpeg：合成音视频
- LangGraph：后续 Agent 工作流编排
- C# WinForms/WPF：后续可作为桌面客户端

## 学习记录

学习过程记录在 [docs/learning-log.md](docs/learning-log.md)。

## 当前状态

项目已封版 1.0，本地 Streamlit 版本可运行。

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

5. 浏览器打开：

```text
http://127.0.0.1:8501
```
