import asyncio
from typing import Any, Dict, List


class WebSearch:
    name = "web"

    async def run(self, **kwargs) -> List[Dict[str, Any]]:
        query = kwargs.get("query", "")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._search, query)

    def _search(self, query: str) -> List[Dict[str, Any]]:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=5))
        return [
            {"title": h.get("title", ""), "url": h.get("href", ""), "snippet": h.get("body", "")}
            for h in hits
        ]


tool = WebSearch()
