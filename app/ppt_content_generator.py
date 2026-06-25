from __future__ import annotations

import json
from typing import Protocol

from app.models import GeneratedSlideContent, PPTGenerationInput, PPTOutlineItem


class LLMClientProtocol(Protocol):
    def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        ...


_CONTENT_SYSTEM_PROMPT = """你是一个专业的 PPT 内容策划专家。
请根据 PPT 大纲生成每页的具体内容，输出 JSON 格式。

输出格式要求：
{
  "slides": [
    {
      "slide_index": 1,
      "title": "页面标题",
      "bullets": ["要点1", "要点2", "要点3"],
      "speaker_hint": "给演讲者的提示，这页怎么讲"
    }
  ]
}

要求：
1. 每页 3-5 个要点，每个要点是一句完整的中文（不是关键词）
2. 要点要具体、有信息量，不要空洞的套话
3. 严禁使用任何形式的占位符，例如 [xxx]、[具体数据]、[...] 等——如果缺乏精确数据，用行业常识给出合理的示例数值
4. speaker_hint 是一句话说明这页怎么讲解
5. 封面页正文要点描述本次分享的核心内容
6. 总页数必须和大纲完全一致
7. 只输出 JSON，不要加 Markdown 代码块标记"""


def _build_content_prompt(
    input_data: PPTGenerationInput,
    outline: list[PPTOutlineItem],
) -> str:
    outline_lines = "\n".join(
        f"  第 {item.slide_index} 页：{item.title}（目的：{item.purpose}）"
        for item in outline
    )
    return f"""请根据以下 PPT 需求和大纲，生成每页的具体内容。

主题：{input_data.topic}
使用场景：{input_data.purpose}
目标受众：{input_data.audience}
风格要求：{input_data.style}
补充说明：{input_data.extra_notes}

大纲：
{outline_lines}

请严格按照 {len(outline)} 页输出，每页 3-5 个要点。"""


def _parse_content_json(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    data = json.loads(text)
    if isinstance(data, dict) and "slides" in data:
        data = data["slides"]
    return data


def generate_content(
    input_data: PPTGenerationInput,
    outline: list[PPTOutlineItem],
    llm_client: LLMClientProtocol,
) -> list[GeneratedSlideContent]:
    prompt = _build_content_prompt(input_data, outline)
    raw = llm_client.generate_with_system(_CONTENT_SYSTEM_PROMPT, prompt)
    items = _parse_content_json(raw)

    if not isinstance(items, list):
        raise ValueError("LLM 返回格式错误，期望 JSON 数组。")

    outline_map = {item.slide_index: item for item in outline}
    result: list[GeneratedSlideContent] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        si = int(item.get("slide_index", len(result) + 1))
        raw_title = str(item.get("title", ""))
        if not raw_title:
            raw_title = outline_map.get(si, outline_map[1]).title
        result.append(
            GeneratedSlideContent(
                slide_index=si,
                title=raw_title,
                bullets=list(str(b) for b in item.get("bullets", [])),
                speaker_hint=str(item.get("speaker_hint", "")),
            )
        )

    if len(result) != len(outline):
        raise ValueError(
            f"LLM 返回了 {len(result)} 页内容，但大纲有 {len(outline)} 页。"
        )

    return result
