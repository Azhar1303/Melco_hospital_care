# agents/tool_registry.py

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, tool):
        self._tools[name] = tool

    def get(self, name: str):
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not registered.")
        return tool

    def has_tool(self, name: str) -> bool:
        return name in self._tools
