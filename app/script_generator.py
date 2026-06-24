from __future__ import annotations

from typing import Protocol, Sequence

from app.models import SlideContent, SlideScript


class LLMClientProtocol(Protocol):
    def generate(self, prompt: str) -> str:
        ...


STYLE_OPTIONS: dict[str, str] = {
    "course": "课程讲解风格：表达清楚、耐心，适合培训和教学。",
    "project_report": "项目汇报风格：结构化、专业，适合作品展示和进度汇报。",
    "interview": "面试讲解风格：突出技术决策、个人负责内容和项目亮点。",
    "sales_pitch": "销售路演风格：更有说服力，适合产品介绍。",
}


def calculate_target_chars(
    total_minutes: int,
    slide_count: int,
    chars_per_minute: int = 200,
) -> int:
    if total_minutes <= 0:
        raise ValueError("目标总时长必须大于 0 分钟。")
    if slide_count <= 0:
        raise ValueError("PPT 至少需要 1 页。")
    return max(10, round(total_minutes * chars_per_minute / slide_count))


def build_prompt(
    slide: SlideContent,
    target_chars: int,
    style_key: str,
    custom_style: str = "",
) -> str:
    style = STYLE_OPTIONS.get(style_key)
    if style is None:
        raise ValueError(f"未知讲稿风格：{style_key}")

    custom_line = ""
    if custom_style.strip():
        custom_line = f"\n用户补充风格要求：{custom_style.strip()}"

    return f"""你是一名专业中文演讲稿作者。请根据下面 PPT 页面内容，生成这一页的中文演讲稿。

讲稿风格：{style}{custom_line}
目标长度：严格 {target_chars} 个中文字符，不得低于 {int(target_chars*0.9)} 字，不得高于 {int(target_chars*1.1)} 字。请确保输出正文的字符数确实在此范围内。

要求：
1. 不要照读 PPT 原文，要补充解释和自然过渡。
2. 只输出演讲稿正文，不要输出标题、编号或 Markdown。
3. 内容要围绕这一页，不要虚构 PPT 中没有依据的具体数据。

PPT 页码：第 {slide.index} 页
PPT 标题：{slide.title or "无标题"}
PPT 内容：
{slide.raw_text}
"""


def generate_scripts(
    slides: Sequence[SlideContent],
    total_minutes: int,
    style_key: str,
    custom_style: str,
    llm_client: LLMClientProtocol,
) -> list[SlideScript]:
    if not slides:
        raise ValueError("没有可生成讲稿的 PPT 页面。")

    target_chars = calculate_target_chars(total_minutes, len(slides))
    results: list[SlideScript] = []

    for slide in slides:
        prompt = build_prompt(slide, target_chars, style_key, custom_style)
        script = llm_client.generate(prompt).strip()
        if not script:
            raise ValueError(f"第 {slide.index} 页 LLM 返回空内容。")
        results.append(
            SlideScript(
                slide_index=slide.index,
                title=slide.title,
                script=script,
                target_chars=target_chars,
                style=style_key,
            )
        )

    return results
