from abc import ABC, abstractmethod
from domain.program_data import ProjectData

class ProgramRepository(ABC):
    @abstractmethod
    async def get_last_update(program_name: str) -> int:
        pass

    @abstractmethod
    async def put_last_update(program_name: str, last_updated: int):
        pass

    @abstractmethod
    async def put_project(project: ProjectData):
        pass