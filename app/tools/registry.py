from typing import Dict, Any, Protocol

class Tool(Protocol):
    name: str
    async def run(self, **kwargs) -> Any: ...

class ToolRegistry: 
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools.get(name)
    
    def has(self, name: str) -> bool:
        return name in self._tools
    

registry =ToolRegistry()