from typing import Dict, Any

class Memory:
    def __init__(self):
        self.store: Dict[str, Any] = {}

    def get(self, key: str, default = None):
        return self.store.get(key, default)
    
    def set(self, key: str, value: Any):
        self.store[key] = value
        return value