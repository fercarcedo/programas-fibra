from abc import ABC, abstractmethod

class ProgramRepository(ABC):
    @abstractmethod
    async def get_last_update(program_name: str) -> int:
        pass

    @abstractmethod
    async def put_last_update(program_name: str, last_updated: int):
        pass