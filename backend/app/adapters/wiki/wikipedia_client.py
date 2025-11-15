# app/adapters/wiki/wikipedia_client.py
from __future__ import annotations

from typing import Tuple
from urllib.parse import quote

import httpx


class WikipediaClient:
    def __init__(self, language: str = "en") -> None:
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/"

    def fetch_summary(self, topic: str) -> Tuple[str | None, str | None]:
        if not topic:
            return None, None

        url = self.base_url + quote(topic)
        try:
            resp = httpx.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            summary = data.get("extract")
            page_url = (
                data.get("content_urls", {})
                .get("desktop", {})
                .get("page")
            )
            return summary, page_url
        except Exception:
            return None, None
