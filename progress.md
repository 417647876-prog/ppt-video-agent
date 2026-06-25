# Progress

## 2026-06-23

- 已进入计划式开发流程。
- 已检查当前目录：暂无项目文件。
- 已确认当前目录不是 Git 仓库。
- 已创建 `task_plan.md`、`findings.md`、`progress.md`。
- 下一步需要用户确认第一版界面和服务选择，再开始创建项目骨架。
- 已将 GitHub 展示和学习过程记录纳入项目计划。
- 已创建 `.gitignore`、`README.md`、`docs/learning-log.md`。
- 已执行 `git init` 初始化本地仓库。
- 已检查 Git 提交配置：当前未设置 `user.name` 和 `user.email`。
- 已检查 GitHub CLI：当前系统未安装 `gh` 命令。
- 已设置本仓库局部 Git 身份：`417647876-prog`。
- 已添加远程仓库：`https://github.com/417647876-prog/ppt-video-agent.git`。
- 已完成首次提交并推送到 GitHub `main` 分支。
- 已确认第一版入口为 Streamlit。
- 已确认第一版路线为 PPT 解析、真实 LLM 讲稿生成和页面预览。
- 已确认 LLM 使用 OpenAI 兼容配置，讲稿风格支持内置选项和自定义补充。
- 已创建设计文档：`docs/superpowers/specs/2026-06-23-streamlit-script-mvp-design.md`。
- 已将 Streamlit MVP 设计文档改为中文，方便 GitHub 展示和学习复盘。
- 已创建 Streamlit 讲稿生成 MVP 实现计划：`docs/superpowers/plans/2026-06-23-streamlit-script-mvp.md`。
- 已创建功能分支：`feature/streamlit-script-mvp`。
- 已完成 Task 1：项目依赖、Python 包入口、基础数据模型和 README 运行说明。
- 已验证依赖安装和 `python -m compileall app tests` 通过。
- 已完成 Task 2：JSON 序列化和本地保存工具。
- 已按 TDD 验证 `tests/test_storage.py` 从失败到通过。
- 已完成 Task 3：目标字数计算、讲稿提示词构建和逐页讲稿生成逻辑。
- 已按 TDD 验证 `tests/test_script_generator.py` 从失败到通过，当前 `pytest -v` 共 6 个测试通过。
- 已完成 Task 4：PPT 文本解析和 OpenAI 兼容 LLM 客户端。
- 已补充 `tests/test_ppt_parser.py` 和 `tests/test_llm_client.py`，当前 `pytest -v` 共 9 个测试通过。
- 已完成 Task 5：Streamlit 页面入口、PPT 上传、讲稿生成预览和 JSON 下载。
- 已执行 `python -m compileall app` 和 `pytest -v`，均通过。
- 已新增语音生成代码：默认使用 Windows 本机中文语音生成 WAV，Edge 在线语音作为可选 MP3 引擎，并打包为 `audio.zip` 下载。
- 已验证音频打包、TTS 调度测试和 Windows 本机语音真实生成通过；Edge 在线语音在当前环境存在 `NoAudioReceived` 不稳定情况。

## 2026-06-25

- 已确认暂不继续做 PPT 生成功能，当前重点回到“已有 PPT -> 演讲稿 -> 语音 -> 视频”的主线优化。
- 已新增版本计划文档：`docs/roadmap-video-pipeline.md`。
- 计划后续优先完善：讲稿可编辑、输出目录和历史记录、任务过程可见化、TTS 稳定性、面试展示文档。
- 已将“每完成一个版本后创建版本分支、推送 GitHub、更新项目文档和学习日志”写入 `docs/roadmap-video-pipeline.md` 和 `docs/learning-log.md`。

## 2026-06-25 Version 1.1

- 分支：`version/1.1-script-editing`
- 状态：已完成，待推送 GitHub
- 验证：pytest -q 55 passed
- 完成：讲稿可编辑、编辑后生成语音和视频、单页重新生成
- 遗留：未做单页重新生成后自动保存（需手动点击保存所有修改）
- 文档：README、project-context、roadmap 已更新

## 2026-06-25 Version 1.2

- 分支：`version/1.2-progress-visibility`
- 状态：本地封版提交已完成，GitHub 推送因网络连接超时暂未完成
- 验证：`pytest -q` 57 passed
- 完成：任务过程可见化、分阶段错误提示、`audio.zip` 下载、`images.zip` 下载、`pytest.ini` 限定测试目录、`ffprobe` 路径修复
- 文档：README、project-context、run-guide、roadmap、learning-log、release note 已更新
- 本地提交：`e16b5d2 feat: complete version 1.2 progress visibility`
- 推送结果：`git push -u origin version/1.2-progress-visibility` 失败，原因是 GitHub HTTPS 连接被重置；`curl -I https://github.com` 也超时
- 下一步：网络恢复后推送 `version/1.2-progress-visibility` 分支和 `v1.2.0` 标签；随后进入 1.3 输出目录和历史记录

## 2026-06-25 Download and Output Planning

- 已新增计划文档：`docs/download-and-output-optimization-plan.md`
- 决策：1.3 将下载区分为“最终结果”和“中间文件下载（调试用）”
- 决策：Streamlit 下载按钮不能稳定强制弹出 Windows 保存位置选择框，保存位置主要由浏览器设置控制
- 决策：1.3 主方案改为每次生成创建独立本地任务目录，并提供完整任务包 `task_package.zip`
- 已将该计划挂到 `docs/roadmap-video-pipeline.md` 的 1.3 章节
