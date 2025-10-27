from domain.repositories.config_repository import ConfigRepository
import json

class KVConfigRepository(ConfigRepository):
    def __init__(self, env):
        self.env = env
        
    async def get_fiber_program_to_url_map(self) -> dict[str, str]:
        url_map = await self.env.CONFIG.get("workflow:fiber-program-url-map")
        return json.loads(url_map)