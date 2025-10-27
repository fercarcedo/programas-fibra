from abc import ABC, abstractmethod

class ConfigRepository(ABC):
    @abstractmethod
    async def get_fiber_program_to_url_map() -> dict[str, str]:
        pass
