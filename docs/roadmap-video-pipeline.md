# 演讲视频生成主线版本计划

> 状态：1.2 任务过程可见化版本已完成。

## 背景

当前项目已经完成本地最小可用闭环：

```text
上传 PPT
 -> 解析每页内容
 -> LLM 生成逐页讲稿
 -> TTS 生成语音
 -> PowerPoint COM 导出页面图片
 -> ffmpeg 合成 MP4 视频
```

接下来不优先扩展“自动生成 PPT”，而是把现有视频生成主线打磨成一个稳定、好演示、适合面试讲解的 AI 应用。

## 总体目标

把项目从“能跑通的 Demo”升级为“可编辑、可追溯、可演示、可解释”的本地 AI 工具。

重点不是增加复杂功能，而是提高以下能力：

- 用户可以控制和修正 LLM 输出
- 长流程执行过程清晰可见
- 生成结果便于保存、复用和回溯
- 语音和视频生成更稳定
- 项目文档适合 GitHub 展示和面试表达

## 版本规划

### ✅ 1.1：讲稿可编辑版本（已完成）

#### 目标

让用户在生成视频前，可以检查和修改每一页讲稿。

#### 功能范围

- 生成讲稿后，在页面中显示每页可编辑文本框
- 用户编辑后，使用编辑后的讲稿生成语音和视频
- 支持下载原始讲稿 `scripts.json`
- 支持下载编辑后讲稿 `scripts_edited.json`
- 支持对单页讲稿重新生成，而不是整份 PPT 重跑

#### 暂不做

- 多人协作编辑
- 富文本编辑器
- 云端保存
- 复杂版本对比

#### 价值

LLM 一次生成不可能每页都完美。加入人工编辑后，项目从“一次性自动生成 Demo”变成“人机协作工具”。

#### 面试表达

> 我没有把大模型输出直接当成最终结果，而是设计了一个可编辑的中间层。用户可以先审阅和修改每页讲稿，再进入 TTS 和视频合成。这体现了我对 AI 应用可控性和人机协作流程的理解。

### ✅ 1.2：任务过程可见化版本（已完成）

### 目标

让用户清楚知道视频生成正在执行哪一步、处理到哪一页、失败在哪里。

### 功能范围

- 明确展示执行阶段：
  - 解析 PPT
  - 生成讲稿
  - 生成语音
  - 导出页面图片
  - 合成视频片段
  - 拼接最终视频
- 每个阶段显示当前进度
- 逐页处理时显示 `第 x / n 页`
- 出错时提示具体阶段和错误原因
- 保留中间结果下载入口：
  - `slides.json`
  - `scripts.json`
  - `scripts_edited.json`
  - 音频压缩包
  - 页面图片压缩包
  - `final.mp4`

### 实际实现

- “先生成演讲稿预览”使用状态条展示解析和 LLM 生成过程
- “一键生成视频”使用 `st.status()` 和 `st.progress()` 展示长流程状态
- 视频片段合成时显示当前页数
- 失败时按当前阶段提示，例如“生成语音失败”“导出页面图片失败”
- 生成完成后可下载：
  - `slides.json`
  - `scripts.json`
  - `scripts_edited.json`
  - `audio.zip`
  - `images.zip`
  - `final.mp4`
- 补充 `pytest.ini`，限制 `pytest -q` 只收集 `tests/` 目录，避免临时脚本被误收集
- 修复 `ffprobe` 路径查找问题，避免读取视频时长阶段误替换目录名

### 暂不做

- 后台任务队列
- 浏览器关闭后继续运行
- 多任务并发

### 价值

视频生成是长流程。如果页面只有一个按钮和一个最终结果，用户会觉得不可控。过程可见化能显著提升产品完成度。

### 面试表达

> 这个项目里有多个耗时步骤。我把长流程拆成可见阶段，并在页面上显示当前进度和失败点，这样用户能知道系统不是卡住了，而是在执行具体任务。

## 1.3：输出目录和历史记录版本

### 目标

让每次生成都有独立任务目录，便于查找、复用和问题排查。

下载区和本地保存的细化设计见：

- `docs/download-and-output-optimization-plan.md`

### 建议目录结构

```text
output/
  20260625_153000_项目汇报/
    input.pptx
    slides.json
    scripts.json
    scripts_edited.json
    audio/
      slide_001.wav
      slide_002.wav
    images/
      slide_001.png
      slide_002.png
    clips/
      clip_001.mp4
      clip_002.mp4
    final.mp4
    run_info.json
```

### 功能范围

- 下载区分为“最终结果”和“中间文件下载（调试用）”
- 支持下载完整任务包 `task_package.zip`
- 每次任务创建独立输出目录
- 保存原始 PPT 副本
- 保存解析结果、讲稿、编辑后讲稿
- 保存音频、图片、视频片段和最终视频
- 生成 `run_info.json`，记录：
  - 任务时间
  - PPT 文件名
  - 页数
  - 讲稿风格
  - TTS 引擎
  - 选择的声音
  - 是否调试模式
  - 最终输出路径
- 页面显示最近生成的任务

### 暂不做

- 数据库
- 用户账号
- 云端文件管理

### 价值

输出目录规范后，项目更像一个真正的本地工具，也方便调试和复盘。

### 面试表达

> 我没有只把最终视频丢到一个文件夹里，而是把每次生成看作一个任务，保存输入、中间结果、最终产物和运行信息。这样方便排查问题，也方便用户回溯每次生成过程。

## 1.4：TTS 稳定性增强版本

### 目标

降低语音生成失败对整个流程的影响。

### 功能范围

- 默认使用 Windows 本机语音作为稳定方案
- Edge、MiniMax、火山语音作为可选高级方案
- 增加“只生成语音”按钮
- TTS 失败时提示用户换引擎或重试
- 单页语音失败时，尽量保留已生成音频
- 页面显示不同 TTS 引擎的说明：
  - Windows：稳定，声音自然度一般
  - Edge：免费，依赖网络，可能不稳定
  - MiniMax / 火山：声音自然，需要 API 配置

### 暂不做

- 自动语音质量评分
- 自动音色推荐
- 字幕时间轴精确对齐

### 价值

演示时语音失败会严重影响体验。先保证稳定，再追求声音自然。

### 面试表达

> 我把 TTS 做成了可替换的接口，并支持多个语音引擎。这样即使某个在线服务失败，也可以切换到本机语音完成演示，保证流程稳定。

## 1.5：面试展示文档版本

### 目标

把项目整理成适合 GitHub 展示和面试表达的材料。

### 建议新增文档

```text
docs/interview-answer.md
docs/architecture-flow.md
docs/demo-script.md
```

### 文档内容

#### `docs/interview-answer.md`

- 项目背景
- 技术栈
- 核心流程
- 难点和解决方案
- 我负责的内容
- 可以继续优化的地方
- 适合 C# 转 AI 应用开发者的表达方式

#### `docs/architecture-flow.md`

- 用户请求从 Streamlit 进入
- 经过哪些函数
- 每个模块负责什么
- 最终如何生成 MP4

#### `docs/demo-script.md`

- 演示前准备
- 如何启动项目
- 上传 PPT
- 生成讲稿
- 编辑讲稿
- 生成视频
- 展示输出目录和最终视频

### 价值

这个项目不只是为了运行，也要服务求职展示。面试文档能帮助你把技术实现讲清楚。

## 推荐实施顺序

当前最推荐的顺序：

1. **1.1 讲稿可编辑版本**（已完成）
2. **1.2 任务过程可见化版本**（已完成）
3. **1.3 输出目录和历史记录版本**
4. **1.4 TTS 稳定性增强版本**
5. **1.5 面试展示文档版本**

原因：

- 讲稿可编辑最能提高真实可用性
- 输出目录规范能支撑后面的过程可见化和错误排查
- 过程可见化让长任务体验更完整
- TTS 稳定性保证演示不翻车
- 面试文档最后整理，更容易基于真实功能来写

## 当前最小下一步

优先做：

```text
创建独立任务目录
 -> 保存 input.pptx / slides.json / scripts.json / scripts_edited.json
 -> 保存 audio/ images/ clips/ final.mp4
 -> 写入 run_info.json
 -> 页面展示最近生成记录
```

这一步将进入 1.3，重点是让每次生成都有可追溯的任务目录。

## 每个版本完成后的固定流程

每完成一个版本，例如 `1.1 讲稿可编辑版本`，都按下面流程收尾。

### 1. 验证功能

先在本地确认功能真的可用：

```powershell
pytest -q
streamlit run app/streamlit_app.py --server.headless true
```

需要手动验证的功能，要在浏览器里实际跑一遍关键流程，例如上传 PPT、生成讲稿、编辑讲稿、生成视频。

### 2. 更新项目文档

至少更新以下文档：

- `README.md`：更新当前功能和运行说明
- `docs/project-context-for-llm.md`：更新当前版本状态、核心流程、关键文件
- `docs/roadmap-video-pipeline.md`：把对应版本标记为已完成，补充实际实现情况
- `docs/run-guide.md`：如果启动方式、配置项、验证方式变化，需要同步更新

如果这个版本适合面试表达，也同步更新：

- `docs/interview-answer.md`
- `docs/architecture-flow.md`
- `docs/demo-script.md`

### 3. 更新学习记录

每个版本完成后，都要更新：

- `docs/learning-log.md`
- `progress.md`

学习日志重点记录：

- 本版本完成了什么
- 遇到了什么问题
- 怎么解决
- 学到了什么工程经验
- 面试时可以怎么讲

### 4. 创建版本分支

版本完成并验证后，从当前工作状态创建一个版本分支。

分支命名建议：

```text
version/1.1-script-editing
version/1.2-progress-visibility
version/1.3-output-history
version/1.4-tts-stability
version/1.5-interview-docs
```

命令示例：

```powershell
git checkout -b version/1.1-script-editing
```

如果已经在功能分支上开发，也可以先合并或直接把当前分支推送为版本分支，具体根据当时工作区状态决定。

### 5. 提交代码

提交前检查：

```powershell
git status --short
pytest -q
```

提交信息建议：

```powershell
git add .
git commit -m "feat: complete version 1.1 script editing"
```

文档单独提交也可以：

```powershell
git commit -m "docs: update version 1.1 notes"
```

### 6. 推送到 GitHub

将版本分支推送到 GitHub：

```powershell
git push -u origin version/1.1-script-editing
```

如果需要，也可以打标签：

```powershell
git tag v1.1.0
git push origin v1.1.0
```

### 7. 版本完成记录

完成后，在 `progress.md` 里记录：

- 版本号
- 分支名
- GitHub 推送状态
- 测试结果
- 主要功能
- 遗留问题

示例：

```markdown
## 2026-06-25 Version 1.1

- 分支：`version/1.1-script-editing`
- 已推送 GitHub
- 验证：`pytest -q` 通过
- 完成：讲稿可编辑、编辑后讲稿生成语音和视频、下载 `scripts_edited.json`
- 遗留：暂未做单页重新生成讲稿
```

