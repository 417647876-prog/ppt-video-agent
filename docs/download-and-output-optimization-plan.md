# 下载区和本地输出目录优化计划

> 适用版本：计划纳入 1.3 “输出目录和历史记录版本”。

## 背景

1.2 已经支持下载多个结果文件：

- `slides.json`
- `scripts.json`
- `scripts_edited.json`
- `audio.zip`
- `images.zip`
- `final.mp4`

但当前页面是把下载按钮平铺在一起，用户不容易区分“最终成果”和“调试文件”。同时，本地保存目前主要保存最终视频，目录结构还不适合后续回溯、重新下载和排查问题。

## 目标

优化两个体验：

1. 页面下载区更清楚，最终成果优先，中间文件收纳到调试区域。
2. 本地保存改为“每次生成一个任务文件夹”，保存输入、中间产物、最终视频和运行信息。

## 下载区设计

### 第一层：最终结果

生成视频后优先展示：

```text
最终结果
[下载 final.mp4]
[下载 scripts_edited.json]
```

说明：

- `final.mp4` 是用户最关心的最终视频。
- `scripts_edited.json` 是最终使用的讲稿，适合复查和复用。
- 如果用户没有编辑讲稿，则按钮文案可以显示为 `下载最终讲稿 scripts.json`。

### 第二层：中间文件下载（调试用）

使用折叠区收纳：

```text
中间文件下载（调试用）
[下载 slides.json]
[下载 scripts.json（原始）]
[下载 audio.zip]
[下载 images.zip]
```

说明：

- 普通用户不一定需要这些文件。
- 开发和排错时很有价值。
- 折叠区可以避免页面显得混乱。

### 第三层：完整任务包

1.3 建议新增：

```text
[下载本次任务全部文件.zip]
```

完整任务包包含：

```text
input.pptx
slides.json
scripts.json
scripts_edited.json
audio/
images/
clips/
final.mp4
run_info.json
```

这是最适合演示和交付的下载方式。

## 关于“点击后弹出选择保存位置”

Streamlit 的 `st.download_button` 本质是浏览器下载，不是 Windows 桌面程序的“另存为”对话框。

因此：

- 是否弹出保存位置选择框，主要由浏览器设置决定。
- 如果浏览器开启了“下载前询问每个文件的保存位置”，点击下载时就会弹出选择保存位置。
- Streamlit 服务端代码不能稳定地强制浏览器弹出 Windows 原生保存对话框。

### 可行方案

#### 方案 A：继续使用浏览器下载

优点：

- 最简单
- 兼容 Streamlit
- 用户熟悉

缺点：

- 是否弹出保存位置由浏览器控制
- 不能由 Python 代码强制指定

建议：

在页面提示：

```text
如果希望每次下载都选择保存位置，请在浏览器设置中开启“下载前询问每个文件的保存位置”。
```

#### 方案 B：保存到项目本地任务目录

优点：

- 程序可控
- 适合本地工具
- 方便历史记录和任务回溯

缺点：

- 文件保存在服务器运行目录，不是浏览器下载目录
- 用户需要知道本地输出路径

建议：

这是 1.3 的主方案。生成完成后页面显示：

```text
本地输出目录：
D:\学习\ppt\output\20260625_223000_高速公路保险方案\
```

并提供：

```text
[复制输出路径]
[下载完整任务包.zip]
```

#### 方案 C：桌面客户端选择保存位置

优点：

- 可以弹出真正的 Windows 文件夹选择框
- 符合 C# WinForms/WPF 使用习惯

缺点：

- 不适合当前 Streamlit Web 页面
- 需要后续做桌面壳或本地客户端

建议：

放到后续 C# 桌面客户端阶段，不纳入当前 1.3。

## 本地输出目录优化

### 当前问题

当前输出更偏“单文件保存”：

```text
output/
  xxx_timestamp.mp4
```

问题：

- 看不出这次任务用了哪个 PPT
- 缺少讲稿、音频、图片等中间文件
- 多次生成后文件夹容易混乱
- 不方便调试和面试展示

### 目标结构

每次生成创建一个独立任务目录：

```text
output/
  20260625_223000_高速公路保险方案/
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
    task_package.zip
    run_info.json
```

### 目录命名规则

建议格式：

```text
YYYYMMDD_HHMMSS_原PPT文件名简化
```

例如：

```text
20260625_223000_高速公路保险培训
```

规则：

- 去掉 `.pptx` 后缀
- 替换 Windows 文件名不允许的字符
- 限制长度，避免路径过长

## `run_info.json` 内容

建议记录：

```json
{
  "created_at": "2026-06-25 22:30:00",
  "input_file": "高速公路保险培训.pptx",
  "slide_count": 12,
  "debug_mode": true,
  "style_key": "course",
  "tts_engine": "windows",
  "voice": "Huihui",
  "target_minutes": 30,
  "actual_minutes": 29.4,
  "output_dir": "D:\\学习\\ppt\\output\\20260625_223000_高速公路保险培训",
  "final_video": "final.mp4"
}
```

价值：

- 方便用户知道这次任务怎么生成的
- 方便开发者排查问题
- 面试时能体现工程化和可追溯设计

## 页面展示建议

生成完成后显示：

```text
生成完成

最终结果
[下载 final.mp4]
[下载最终讲稿]

本地输出目录
D:\学习\ppt\output\20260625_223000_高速公路保险培训\

[下载完整任务包.zip]

中间文件下载（调试用）
[下载 slides.json]
[下载 scripts.json]
[下载 audio.zip]
[下载 images.zip]
```

## 1.3 最小实现范围

1.3 建议只做这些：

- 下载区分为“最终结果”和“中间文件下载（调试用）”
- 每次生成创建独立任务目录
- 保存 `input.pptx`
- 保存 `slides.json`
- 保存 `scripts.json`
- 保存 `scripts_edited.json`
- 保存 `audio/`
- 保存 `images/`
- 保存 `clips/`
- 保存 `final.mp4`
- 生成 `run_info.json`
- 生成 `task_package.zip`
- 页面显示本地输出目录

暂不做：

- 数据库历史记录
- 多任务并发
- 真正的 Windows 文件夹选择对话框
- 云端同步

## 后续增强

1.4 或更后面可以考虑：

- 页面显示最近 5 次任务
- 从历史任务中重新下载 `final.mp4`
- 删除历史任务
- 打开本地输出目录按钮
- C# WinForms/WPF 桌面壳中加入真正的文件夹选择对话框

