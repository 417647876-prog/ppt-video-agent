# Findings

## 2026-06-23

- 当前目录 `D:\学习\ppt` 为空目录。
- 当前目录不是 Git 仓库。
- 项目适合按流水线开发：PPT 解析 -> 讲稿生成 -> TTS -> 图片导出 -> ffmpeg 合成 -> Agent 编排。
- 不建议第一版直接做多 Agent。更稳的路径是先做普通 Python 流水线，再用 LangGraph 包装为单 Agent 工具流。
- 对学习者更友好的方案是：Python 负责 AI 和视频处理，C# WinForms/WPF 后续作为桌面壳调用本地服务。

## 技术风险

- PPT 转图片在 Windows 上有多种方式：PowerPoint COM 效果好但依赖 Office；LibreOffice 更适合自动化但可能有格式差异。
- TTS 平台价格和调用限制差异较大，第一版应通过接口抽象避免绑定死。
- 2 小时视频属于长任务，后续需要任务状态、断点续跑和日志。
