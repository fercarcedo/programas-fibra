from datetime import datetime, timezone
from email.utils import format_datetime

from domain.repositories.program_repository import ProgramRepository
from domain.program_data import ProjectData
from domain.projects_status import ProjectsStatus
from infrastructure.entity.projects_status_entity import projects_status_to_dict
from infrastructure.repositories.mapper.project_mapper import from_entity, to_entity
from infrastructure.repositories.mapper.project_status_mapper import to_entity as project_status_to_entity
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
        await self.env.PROJECTS.put(project.project, json.dumps(project_entity.to_dict()))

    async def put_projects_status(self, projects_status: ProjectsStatus):
        projects_status_entity = project_status_to_entity(projects_status)
        summary_string = json.dumps(projects_status_to_dict(projects_status_entity))
        await self.env.PROJECTS.put("projects-status", summary_string)
        last_modified = format_datetime(datetime.now(timezone.utc), usegmt=True)
        await self.env.PROJECTS.put("projects-status:last-modified", last_modified)

    async def find_projects(self) -> list[ProjectData]:
        projects = []
        cursor = None
        
        while cursor is not None or not projects:
            result = await self.env.PROJECTS.list(prefix="TSI-", cursor=cursor)
            projects.extend([
                from_entity(await self.env.PROJECTS.get(key_item.name, "json"), key_item.name)
                for key_item in result.keys
            ])
            cursor = result.cursor
        
        return projects

