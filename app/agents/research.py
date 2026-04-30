from typing import Dict, Any
from app.tools.registry import registry

class ResearchAgent:
    name = "research"

    async def web_search(self, context: Dict[str, Any]):
        web = registry.get("web")
        query = context.get("query", "competitor pricing")
        results = await web.run(query=query)
        context["sources"] = results
        return {"results": results}

    async def summarize(self, context: Dict[str, Any]):
        sources = context.get("sources", [])
        summary = "\n".join(f"- {s['title']}: {s['snippet']}" for s in sources)
        context["summary"] = summary
        return {"summary": summary}