from abc import ABC, abstractmethod
from domain.program_data import ProjectData
from domain.projects_status import ProjectsStatus

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

    @abstractmethod
    async def find_projects() -> list[ProjectData]:
        pass

    @abstractmethod
    async def put_projects_status(projects_status: ProjectsStatus):
        pass

    @abstractmethod
    async def get_last_xlsx_digest(self, program_name: str) -> str | None:
        pass

    @abstractmethod
    async def put_last_xlsx_digest(self, program_name: str, digest: str):
        pass

    @abstractmethod
    async def put_aggregated(self, projects_data: list[ProjectData]):
        pass