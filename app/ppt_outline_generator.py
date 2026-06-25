from __future__ import annotations

import json
from typing import Protocol

from app.models import PPTGenerationInput, PPTOutlineItem, ReferenceContext


class LLMClientProtocol(Protocol):
    def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        ...


_OUTLINE_SYSTEM_PROMPT = """你是一个专业的 PPT 大纲策划专家。
请根据用户需求生成 PPT 大纲，输出 JSON 格式。

输出格式要求（严格 JSON 数组）：
[
  {
    "slide_index": 1,
    "title": "页面标题",
    "purpose": "这一页要表达什么目的"
  }
]

要求：
1. 标题简洁有力，能概括该页核心内容
2. purpose 说明这一页想传达什么，不是正文内容
3. 总页数必须和用户要求的完全一致
4. 第 1 页必须是封面页，标题体现整体主题
5. 必须围绕用户的具体行业和场景来设计大纲，不要输出通用模板
6. 只输出 JSON，不要加 Markdown 代码块标记"""


def _build_outline_prompt(input_data: PPTGenerationInput) -> str:
    return f"""请根据以下需求生成一份 {input_data.slide_count} 页的 PPT 大纲。

主题：{input_data.topic}
使用场景：{input_data.purpose}
目标受众：{input_data.audience}
风格要求：{input_data.style}
补充说明：{input_data.extra_notes}

请输出 {input_data.slide_count} 页大纲，严格按照 JSON 数组格式。"""


def _build_outline_with_reference_prompt(
    input_data: PPTGenerationInput,
    reference: ReferenceContext,
) -> str:
    ref_lines = "\n".join(
        f"  第 {s['index']} 页：{s['title']}"
        for s in reference.slides_summary
    )
    style_line = ""
    if reference.company_name or reference.style_notes:
        style_line = f"\n参考 PPT 的风格特征：{reference.style_notes}"
    return f"""请根据以下需求生成一份 PPT 大纲，参考已有 PPT 的结构和节奏。

    新 PPT 主题：{input_data.topic}
使用场景：{input_data.purpose}
目标受众：{input_data.audience}
风格要求：{input_data.style}
补充说明：{input_data.extra_notes}{style_line}

参考 PPT 共有 {reference.slide_count} 页，结构如下：
{ref_lines}

要求：
1. 新 PPT 的页数可与参考 PPT 不同（参考 {reference.slide_count} 页）
2. 保持参考 PPT 的叙述节奏和逻辑结构
3. 内容根据新主题重新生成，不要照搬参考的标题
4. 第 1 页是封面页
5. 严格按照 JSON 数组格式输出"""


def _parse_outline_json(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def _json_to_outline_items(raw_json: list[dict]) -> list[PPTOutlineItem]:
    result: list[PPTOutlineItem] = []
    for item in raw_json:
        if not isinstance(item, dict):
            continue
        result.append(
            PPTOutlineItem(
                slide_index=int(item.get("slide_index", len(result) + 1)),
                title=str(item.get("title", "")),
                purpose=str(item.get("purpose", "")),
            )
        )
    if not result:
        raise ValueError("无法解析 LLM 返回的大纲内容。")
    return result


def generate_outline(
    input_data: PPTGenerationInput,
    llm_client: LLMClientProtocol,
) -> list[PPTOutlineItem]:
    system = _OUTLINE_SYSTEM_PROMPT + (
        f"\n\n本次 PPT 主题领域：{input_data.topic}。"
        f"\n所有大纲必须围绕「{input_data.topic}」设计，不得偏离。"
    )
    prompt = _build_outline_prompt(input_data)
    raw = llm_client.generate_with_system(system, prompt)
    return _json_to_outline_items(_parse_outline_json(raw))


def generate_outline_with_reference(
    input_data: PPTGenerationInput,
    reference: ReferenceContext,
    llm_client: LLMClientProtocol,
) -> list[PPTOutlineItem]:
    """根据用户要求和参考 PPT 结构生成新大纲"""
    system = _OUTLINE_SYSTEM_PROMPT + (
        f"\n\n本次 PPT 主题领域：{input_data.topic}。"
        f"\n所有大纲必须围绕「{input_data.topic}」设计，不得偏离。"
    )
    prompt = _build_outline_with_reference_prompt(input_data, reference)
    raw = llm_client.generate_with_system(system, prompt)
    return _json_to_outline_items(_parse_outline_json(raw))
