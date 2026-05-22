from __future__ import annotations

from typing import Optional

from config import Config
from openai import OpenAI


class LocalLLMTool:
    """Handles interaction with the local LLM API"""

    def __init__(self):
        self.config = Config()
        self.client = OpenAI(base_url=self.config.LOCAL_LLM_BASE_URL, api_key=self.config.LOCAL_LLM_API_KEY)
        self.model = self.config.LOCAL_LLM_MODEL

    def call_local_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the local LLM with the given prompts and return the response text"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"{{\"error\": \"LLM API error: {str(e)}\"}}"


if __name__ == "__main__":
    # Simple test when running this file directly
    parser = LocalLLMTool()
    result = parser.call_local_llm(
        system_prompt="You are a helpful assistant. Output only the answer.",
        user_prompt="What is 2+2?"
    )
    print(f"LLM Response: {result}")
