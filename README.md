# AI PPT 演讲视频生成器

这是一个面向学习和求职展示的 AI 应用项目。目标是把一个本地 PPT 文件自动生成带讲稿、配音、字幕和视频合成结果的演讲视频。

## 项目目标

用户上传或选择一个 `.pptx` 文件后，系统自动完成：

1. 解析每页 PPT 内容
2. 根据目标总时长生成逐页演讲稿
3. 生成每页语音
4. 导出每页画面
5. 合成最终 MP4 视频

## 第一版范围

第一版优先做本地最小闭环：

- 本地读取 `.pptx`
- 生成 `slides.json`
- 生成逐页讲稿
- 预留 TTS 接口
- 使用 ffmpeg 合成视频
- 后续再接 LangGraph 做 Agent 编排

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

项目处于计划和骨架设计阶段，尚未进入业务代码开发。
