class WebMock:
    name = "web"
    async def run(self, **kwargs):
        q = kwargs.get("query", "")
        return [{"title": "Competitor Pricing 2025", "url": "https://example.com/a", "snippet": f"Findings for {q}"}]

tool = WebMock()