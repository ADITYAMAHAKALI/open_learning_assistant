# app/adapters/llm/gemini_provider.py
from typing import Tuple, List
from google import genai
from app.adapters.llm.base import LLMClient

class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def chat(self, prompt: str) -> str:
        # google-genai is sync; wrap in thread executor if you want real async
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return resp.text

    async def chat_with_followups(self, prompt: str) -> Tuple[str, List[str]]:
        full_prompt = f"""
{prompt}

After answering, suggest 3 short followup questions.
Return JSON with keys: answer, followups.
"""
        resp = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
        )
        import json
        parsed = json.loads(resp.text)
        return parsed["answer"], parsed.get("followups", [])
