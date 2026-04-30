from typing import Dict, Any, List

class Agent: 
    name: str = "base"
    tools: List[str] = []

    async def plan(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"steps": []}
    
    async def act(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "noop"}