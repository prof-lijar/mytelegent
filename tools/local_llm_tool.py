from __future__ import annotations

import logging
from openai import OpenAI
from tools.config import Config

# Setup basic logging for the LLM tool
logger = logging.getLogger(__name__)

class LocalLLMTool:
    \"\"\"Tool to communicate with a local LLM (Ollama).\"\"\"

    def __init__(self):
        # Validate configuration before initializing client
        Config.validate_llm_config()
        
        self.client = OpenAI(
            base_url=Config.LOCAL_LLM_BASE_URL,
            api_key=Config.LOCAL_LLM_API_KEY,
            timeout=30.0,
        )

    def call_local_llm(self, system_prompt: str, user_prompt: str) -> str:
        \"\"\"
        Generate a response from the local LLM.
        
        Args:
            system_prompt: The system instructions for the LLM.
            user_prompt: The user query or input.
            
        Returns:
            The LLM's response text.
        \"\"\"
        try:
            response = self.client.chat.completions.create(
                model=Config.LOCAL_LLM_MODEL,
                messages=[
                    {\"role\": \"system\", \"content\": system_prompt},
                    {\"role\": \"user\", \"content\": user_prompt},
                ],
                temperature=0,
            )
            return response.choices[0].message.content or \"\"
        except Exception as e:
            logger.error(f\"Error calling local LLM: {e}\")
            return f\"Error: {str(e)}\"

if __name__ == \"__main__\":
    # Simple manual test for LocalLLMTool
    # Note: This requires Ollama to be running and the model to be specified in Config
    print(\"Testing LocalLLMTool...\")
    try:
        llm = LocalLLMTool()
        sys_prompt = \"You are a helpful assistant.\"
        user_prompt = \"Hello, who are you?\"
        result = llm.call_local_llm(sys_prompt, user_prompt)
        print(f\"Response: {result}\")
    except Exception as e:
        print(f\"Error during test: {e}\")
