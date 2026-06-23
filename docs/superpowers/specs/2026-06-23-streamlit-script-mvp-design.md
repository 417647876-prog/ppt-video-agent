# Streamlit 讲稿生成 MVP 设计

## 目标

开发 AI PPT 演讲视频生成器的第一个可运行版本。第一版使用 Streamlit 做网页入口，把用户上传的 `.pptx` 文件转换成逐页演讲稿，并在页面中展示和导出结果。

这个版本只解决一个核心问题：

```text
PPT 内容 -> AI 生成逐页讲稿
```

语音、字幕、视频合成、数字人和 Agent 编排都放到后续阶段。

## 范围

本版本包含：

- 在 Streamlit 页面上传本地 `.pptx` 文件。
- 输入目标总时长，单位为分钟。
- 选择内置讲稿风格，或填写自定义风格说明。
- 提取每一页 PPT 中可读取的文本。
- 调用 OpenAI 兼容的 LLM API 生成每页讲稿。
- 在网页中预览每页原文和生成讲稿。
- 保存并下载 `slides.json` 和 `scripts.json`。

本版本不包含：

- TTS 语音生成。
- MP4 视频合成。
- 数字人视频。
- 用户账号。
- 云端部署。
- LangGraph 工作流编排。

## 用户流程

1. 用户打开 Streamlit 网页。
2. 用户上传一个 `.pptx` 文件。
3. 用户输入目标总时长，例如 `120` 分钟。
4. 用户选择一种内置讲稿风格：
   - 课程讲解风格
   - 项目汇报风格
   - 面试讲解风格
   - 销售路演风格
5. 用户可以填写自定义风格补充说明。
6. 用户点击“生成讲稿”。
7. 程序提取 PPT 每页文本，并估算每页目标字数。
8. 程序逐页调用配置好的 LLM。
9. 页面展示每页 PPT 原文和 AI 生成讲稿。
10. 用户下载 JSON 结果文件。

## 架构

MVP 是一个由 Streamlit 包装的本地流水线：

```text
Streamlit 页面
  -> PPT 解析
  -> 时长和字数规划
  -> 讲稿提示词构建
  -> OpenAI 兼容 LLM 客户端
  -> JSON 保存和下载
```

设计原则：

- PPT 解析、字数计算、JSON 保存这些步骤必须是确定性的普通 Python 函数。
- 只有“讲稿生成”这一步依赖 LLM。
- 页面代码只负责交互，不直接写 PPT 解析和 LLM 请求细节。
- 每个模块职责清楚，方便后续替换成 Agent 工具。

## 文件结构

第一版使用下面的结构：

```text
app/
  streamlit_app.py
  ppt_parser.py
  script_generator.py
  llm_client.py
  models.py
  storage.py
tests/
  test_ppt_parser.py
  test_script_generator.py
.env.example
requirements.txt
```

### `app/streamlit_app.py`

职责：

- 显示页面标题和布局。
- 接收 PPT 上传。
- 接收目标时长和讲稿风格。
- 调用流水线函数。
- 展示生成结果。
- 提供下载按钮。

这个文件不负责 PPT 解析细节，也不负责 LLM API 请求细节。

### `app/ppt_parser.py`

职责：

- 加载 `.pptx` 文件。
- 提取每页页码、标题和正文文本。
- 返回结构化的幻灯片数据。

第一版只处理普通文本框和标题字段。表格、图表、SmartArt、动画和演讲者备注明确不在本 MVP 范围内。

### `app/script_generator.py`

职责：

- 根据目标总时长计算每页目标字数。
- 为每一页构建 LLM 提示词。
- 调用 `LLMClient`。
- 返回逐页讲稿结果。

中文演讲语速默认按每分钟 `220` 个中文字符计算。例如 60 页 PPT、目标 120 分钟，平均每页约 `440` 个中文字符。

### `app/llm_client.py`

职责：

- 从环境变量读取 API 配置。
- 调用 OpenAI 兼容的 chat completions 接口。
- 返回模型生成的文本。

需要的环境变量：

```text
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
```

代码不能写死 DeepSeek。DeepSeek 只是第一阶段推荐测试服务，后续可以换成 OpenAI、通义千问、智谱、Kimi 或其他兼容接口。

### `app/models.py`

职责：

- 定义共享数据结构。

第一版至少包含：

- `SlideContent`
- `SlideScript`

第一版使用 dataclass 即可，不需要上复杂模型层。

### `app/storage.py`

职责：

- 将幻灯片和讲稿对象转换成 JSON。
- 保存本地输出文件。
- 为 Streamlit 下载按钮准备 JSON 字节内容。

## 讲稿风格

内置风格：

- `course`：课程讲解风格，清楚、耐心，适合培训和教学。
- `project_report`：项目汇报风格，结构化、专业，适合作品展示和进度汇报。
- `interview`：面试讲解风格，突出技术决策、个人负责内容和项目亮点。
- `sales_pitch`：销售路演风格，更有说服力，适合产品介绍。

自定义风格说明应该追加到内置风格后面，而不是完全替换内置风格。这样既能保证输出稳定，也能给用户调整空间。

## 错误处理

页面需要给出清晰错误提示：

- 没有配置 API Key。
- 上传的文件不是 `.pptx`。
- PPT 中没有可提取的文本。
- LLM API 请求失败。
- LLM 返回空内容。

错误信息要同时满足两个要求：

- 普通用户能看懂。
- 开发者能根据错误定位问题。

## 测试

第一版优先测试确定性逻辑：

- 目标时长到每页目标字数的计算。
- 提示词中包含幻灯片文本、讲稿风格和目标长度。
- JSON 序列化结构正确。

PPT 解析可以使用一个最小测试文件或测试辅助函数。LLM 调用必须 mock，测试不能依赖真实 API Key。

## 完成标准

当下面条件全部满足时，MVP 视为完成：

- 可以通过 `streamlit run app/streamlit_app.py` 启动本地网页。
- 可以上传 `.pptx` 文件。
- 页面能展示提取出的 PPT 文本。
- 页面能调用已配置的 LLM 并展示逐页讲稿。
- 用户可以下载 `slides.json` 和 `scripts.json`。
- 确定性模块的测试可以通过。

## 后续阶段

MVP 完成后，再按下面顺序扩展：

1. 增加讲稿手动编辑和项目文件夹保存。
2. 增加 TTS 语音生成。
3. 增加 PPT 页面图片导出。
4. 增加 ffmpeg MP4 视频合成。
5. 使用 LangGraph 把流水线包装成单 Agent 工作流。
