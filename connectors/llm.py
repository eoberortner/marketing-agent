import os

from openai import OpenAI
from typing import List, Dict
from abc import ABC


class LLMClient(ABC):
    def __init__(self, llm_provider: str):
        self.llm_provider = llm_provider


class DeepSeekClient(LLMClient):
    """Objects of this class can interact with the DeepSeek API."""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        """Constructor"""

        super().__init__("DeepSeek")
        if api_key is None:
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
        else:
            self.api_key = api_key

        self.client = OpenAI(
            api_key=self.api_key, base_url="https://api.deepseek.com"
        )
        self.model = model

    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 1500,
        timeout: int = 60,
    ):
        """
        messages: List of messages in format:
            [{"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": "What's the weather today?"}]
        """

        # print(f"[{self.llm_provider}] Sending messages to OpenAI API...{messages}")

        try:
            import time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model, 
                messages=messages,
                timeout=timeout
            )

            response_content = response.choices[0].message.content
            elapsed = time.time() - start_time
            print(f"[{self.llm_provider}] chat responded in {elapsed:.2f}s...{response_content[:100]}...")

            return response_content

        except Exception as e:
            print(f"[{self.llm_provider}] Error in chat: {e}")
            return f"Error: {e}"

    def summarize(self, agent_description: str, task_description: Dict) -> str:
        """gets an image, base64 encoded and calls the OpenAI API
        to describe the image. Then, it returns the description as string."""

        prompt = "Summarize the following information in detail."

        messages = [
            {
                "role": "system",
                "content": agent_description,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "text", "text": task_description},
                ],
            },
        ]

        response = self.chat(messages=messages)

        if isinstance(response, str):
            return response

        return response.choices[0].message.content
