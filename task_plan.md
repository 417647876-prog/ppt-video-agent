# AI PPT 演讲视频生成器开发计划

## 目标

开发一个最小可用版本：用户选择一个 `.pptx` 文件，系统读取每页内容，生成逐页讲稿，生成或接入语音，最后合成为一个 MP4 演讲视频。

## 第一版范围

- 输入：本地 `.pptx` 文件
- 输出：本地 `final.mp4`
- 目标用户：正在学习 AI 应用开发、熟悉 C# WinForms、希望用 Python 打通 AI 流程的开发者
- 第一版不做数字人、不做账号系统、不做云端部署

## 推荐技术路线

- UI：第一阶段先用命令行或 Streamlit；第二阶段再接 C# WinForms/WPF
- 后端语言：Python
- Agent 编排：第一阶段不用复杂多 Agent，先用普通流水线；第二阶段用 LangGraph 包装
- PPT 解析：python-pptx
- 讲稿生成：LLM API，可先做接口抽象
- 语音合成：先做 TTS 接口抽象，具体服务可接 OpenAI TTS、Azure、讯飞或火山
- 视频合成：ffmpeg
- 状态存储：本地文件夹 + JSON，后续再加 SQLite

## 阶段计划

### Phase 1：项目骨架

状态：pending

- 创建 Python 项目结构
- 创建输入、输出、临时文件目录约定
- 添加依赖管理文件
- 添加基础 README

### Phase 2：PPT 解析

状态：pending

- 读取 `.pptx`
- 提取每页标题和文本框内容
- 输出 `slides.json`
- 为 PPT 解析写一个最小测试

### Phase 3：讲稿生成

状态：pending

- 根据页数和目标总时长计算每页目标字数
- 为每页生成讲稿
- 第一版可以先用规则生成占位讲稿，后续替换成 LLM
- 输出 `scripts.json`

### Phase 4：语音生成

状态：pending

- 定义 TTS 接口
- 第一版可以先支持本地占位音频或一个具体 TTS 服务
- 每页输出一个音频文件

### Phase 5：PPT 页面导出图片

状态：pending

- 将每页 PPT 导出成图片
- Windows 本机优先考虑 PowerPoint COM 或 LibreOffice
- 输出 `slide_001.png`、`slide_002.png`

### Phase 6：视频合成

状态：pending

- 使用 ffmpeg 将单页图片和单页音频合成片段
- 拼接所有片段
- 输出 `final.mp4`

### Phase 7：Agent 化

状态：pending

- 将每个阶段包装成工具函数
- 用 LangGraph 定义流程节点
- 支持失败后从指定阶段重跑

## 当前决策

- 先做单机本地版，不做 Web SaaS
- 先做普通流水线，再做 Agent 编排
- 先保证能生成 MP4，再优化讲稿质量和界面
- 第一版入口确定为 Streamlit 网页版
- 第一版实现路线确定为：PPT 解析 + 真实 LLM 讲稿生成 + 页面预览
- 第一版 LLM 接入方式确定为 OpenAI 兼容配置，不绑定具体平台
- 第一版讲稿风格支持内置选项和自定义补充说明
- 第一版暂不做 TTS、视频合成、数字人和 LangGraph 编排

## 待确认问题

- 用户确认设计文档后，进入实现计划编写
- 实际测试时使用哪个 OpenAI 兼容 LLM 服务和模型

## 错误记录

暂无。

## GitHub 和学习过程记录计划

状态：in_progress

- 将项目代码、规划文件和学习日志一起放入 Git 仓库
- 使用 `README.md` 说明项目背景、目标、技术栈和当前进度
- 使用 `docs/learning-log.md` 记录学习过程，方便后续面试复盘
- 使用小步提交记录成长过程，例如：
  - `docs: add project plan`
  - `feat: parse ppt slides`
  - `feat: generate slide scripts`
  - `feat: render video with ffmpeg`
- 暂不上传 `.env`、临时音频、生成视频、PPT 原始素材等大文件或敏感文件
