from abc import ABC, abstractmethod

class PageRenderer(ABC):
    @abstractmethod
    async def render(self, url: str) -> str:
        pass
