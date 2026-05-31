from typing import Dict, Any


class Memory:
    def __init__(self):
        self.store: Dict[str, Any] = {}

    def get(self, key: str, default=None):
        return self.store.get(key, default)

    def set(self, key: str, value: Any):
        self.store[key] = value
        return value

    def delete(self, key: str) -> None:
        self.store.pop(key, None)

    def clear(self) -> None:
        self.store.clear()

    def all(self) -> Dict[str, Any]:
        return dict(self.store)


# Module-level singleton shared across requests within the same process.
shared_memory = Memory()