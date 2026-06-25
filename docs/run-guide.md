# 项目运行方式

## 启动

```powershell
cd D:\学习\ppt
streamlit run app/streamlit_app.py --server.headless true
```

`--server.headless true` 阻止 Streamlit 自动打开系统默认浏览器。

## 停止

```powershell
Get-Process -Name "streamlit" | Stop-Process -Force
```

## 验证服务状态

```powershell
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8501
# 返回 200 即正常
```

## 测试

```powershell
cd D:\学习\ppt
pytest -q
# 预期输出：57 passed
```

## 安装依赖

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
# 编辑 .env 填写 LLM 配置
```

## 当前页面功能

- **上传 PPT 文件**（原有流程）：
  - 上传已有 PPT → 生成讲稿 → 编辑讲稿 → 生成语音 → 导出图片 → 合成视频
  - “先生成演讲稿预览”会显示讲稿生成阶段
  - “一键生成视频”会显示解析、语音、导图、合成、拼接等阶段
  - 生成结果支持下载 `slides.json`、`scripts.json`、`scripts_edited.json`、`audio.zip`、`images.zip` 和 `final.mp4`

PPT 生成功能当前已暂停，相关代码保留在 `app/` 目录中供后续复用。

## 已知问题

1. **PowerShell 管道中文编码**：`@"..."@ | python` 会破坏中文字符。应先把 Python 脚本写入 `.py` 文件再执行。
2. **DeepSeek JSON mode**：`response_format={"type":"json_object"}` 会让模型忽略 user prompt。当前已去掉此设置，靠 prompt 要求 JSON。
3. **Expander 嵌套**：`st.expander` 不能嵌套，当前用 `st.markdown("---")` 替代内层 expander。

## 更多信息

详细项目说明见 `docs/project-context-for-llm.md`。
