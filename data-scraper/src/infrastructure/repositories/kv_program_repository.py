from domain.repositories.program_repository import ProgramRepository
from domain.program_data import ProjectData
from infrastructure.repositories.mapper.project_mapper import to_entity
import json

class KVProgramRepository(ProgramRepository):
    def __init__(self, env):
        self.env = env

    async def get_last_update(self, program_name: str) -> int:
        last_update = await self.env.PROJECTS.get(f"programs:{program_name}:last-updated")
        if not last_update:
            return None
        try:
            return int(last_update)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Last update for {program_name} was not a valid number")

    async def put_last_update(self, program_name: str, last_updated: int):
        await self.env.PROJECTS.put(f"programs:{program_name}:last-updated", last_updated)

    async def put_project(self, project: ProjectData):
        project_entity = to_entity(project)
        print(project_entity)
        await self.env.PROJECTS.put(project.project, json.dumps(project_entity.to_dict()))