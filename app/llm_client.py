from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str


class OpenAICompatibleLLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    @classmethod
    def from_env(
        cls,
        *,
        load_dotenv_file: bool = True,
        dotenv_path: str | Path | None = None,
    ) -> "OpenAICompatibleLLMClient":
        if load_dotenv_file:
            load_dotenv(dotenv_path=dotenv_path, override=True)

        base_url = os.getenv("LLM_BASE_URL", "").strip()
        api_key = os.getenv("LLM_API_KEY", "").strip()
        model = os.getenv("LLM_MODEL", "").strip()

        missing = [
            name
            for name, value in {
                "LLM_BASE_URL": base_url,
                "LLM_API_KEY": api_key,
                "LLM_MODEL": model,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"缺少 LLM 环境变量：{', '.join(missing)}")

        return cls(LLMConfig(base_url=base_url, api_key=api_key, model=model))

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的中文 PPT 演讲稿生成助手。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if content is None or not content.strip():
            raise ValueError("LLM 返回空内容。")
        return content.strip()

    def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        if content is None or not content.strip():
            raise ValueError("LLM 返回空内容。")
        return content.strip()
