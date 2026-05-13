from abc import ABC, abstractmethod

class EmailNotifier(ABC):
    @abstractmethod
    async def send_alert(self, subject: str, body: str) -> None:
        pass
