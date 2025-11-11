# app/adapters/llm/ollama_provider.py
import httpx
from typing import Tuple, List
from app.adapters.llm.base import LLMClient

class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]

    async def chat_with_followups(self, prompt: str) -> Tuple[str, List[str]]:
        combined_prompt = f"""
{prompt}

After answering, suggest 3 short followup questions for the student.
Return JSON with:
- "answer": string
- "followups": list of strings
"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": combined_prompt}],
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"]

        # you can tighten this later with a json schema
        # for now assume the model returns valid JSON
        import json
        parsed = json.loads(content)
        return parsed["answer"], parsed.get("followups", [])
