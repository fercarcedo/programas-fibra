from datetime import datetime, timezone
from email.utils import format_datetime

from domain.repositories.program_repository import ProgramRepository
from domain.program_data import ProjectData
from domain.projects_status import ProjectsStatus
from infrastructure.entity.project_entity import ProjectEntity
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
        await self.env.PROJECTS.put(project.project, json.dumps(project_entity.to_dict(), ensure_ascii=False))

    async def put_projects_status(self, projects_status: ProjectsStatus):
        projects_status_entity = project_status_to_entity(projects_status)
        summary_string = json.dumps(projects_status_to_dict(projects_status_entity))
        await self.env.PROJECTS.put("projects-status", summary_string)
        last_modified = format_datetime(datetime.now(timezone.utc), usegmt=True)
        await self.env.PROJECTS.put("projects-status:last-modified", last_modified)

    async def find_projects(self) -> list[ProjectData]:
        projects = []
        cursor = None
        list_complete = False

        while not list_complete:
            result = await self.env.PROJECTS.list(prefix="TSI-", cursor=cursor)
            projects.extend([
                from_entity(ProjectEntity.from_dict(json.loads(await self.env.PROJECTS.get(key_item.name))), key_item.name)
                for key_item in result.keys
            ])

            list_complete = getattr(result, 'list_complete', True)
            cursor = getattr(result, 'cursor', None)

        return projects

    async def get_last_xlsx_digest(self, program_name: str) -> str | None:
        digest = await self.env.PROJECTS.get(f"programs:{program_name}:xlsx-digest")
        return digest if digest else None

    async def put_last_xlsx_digest(self, program_name: str, digest: str):
        await self.env.PROJECTS.put(f"programs:{program_name}:xlsx-digest", digest)

    async def put_aggregated(self, projects_data: list[ProjectData]):
        aggregated = await self.env.BUCKET_GEO.get("aggregated.json")
        if not aggregated:
            return

        aggregated_data = json.loads(await aggregated.text())

        hexagons_projects_data = await self.env.BUCKET_GEO.get("hexagons_projects.json")
        hexagons_projects = {}
        if hexagons_projects_data:
            hexagons_projects = json.loads(await hexagons_projects_data.text())

        projects_map = {project.project: project for project in projects_data}

        for item in aggregated_data:
            for grantee, programs in item.get("counts", {}).items():
                for program_name, program_info in programs.items():
                    program_info["statuses"].clear()
                    program_info["total"] = 0

        for item in aggregated_data:
            h3_index = item.get("h3Index")
            projects_in_hex = hexagons_projects.get(h3_index, {})

            for project_id, point_count in projects_in_hex.items():
                if project_id not in projects_map:
                    continue

                project = projects_map[project_id]
                grantee = project.grantee
                program_name = project.program_name

                if not grantee or not program_name:
                    continue

                if grantee in item.get("counts", {}) and program_name in item["counts"][grantee]:
                    program_info = item["counts"][grantee][program_name]
                    status_str = project.status.value if hasattr(project.status, "value") else str(project.status)

                    if status_str not in program_info["statuses"]:
                        program_info["statuses"][status_str] = 0
                    program_info["statuses"][status_str] += point_count
                    program_info["total"] += point_count

        await self.env.BUCKET_GEO.put("aggregated.json", json.dumps(aggregated_data, ensure_ascii=False))

