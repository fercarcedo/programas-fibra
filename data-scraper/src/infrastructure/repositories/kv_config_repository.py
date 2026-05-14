from domain.repositories.config_repository import ConfigRepository
import json

class KVConfigRepository(ConfigRepository):
    def __init__(self, env):
        self.env = env
        
    async def get_fiber_program_to_url_map(self) -> dict[str, str]:
        raw = await self.env.CONFIG.get("workflow:fiber-program-url-map")
        entries = json.loads(raw)
        result = {}
        for name, value in entries.items():
            if isinstance(value, str):
                result[name] = value
            elif value.get("active", False):
                result[name] = value["url"]
        return result