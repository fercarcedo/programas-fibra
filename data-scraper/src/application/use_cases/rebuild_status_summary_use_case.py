from domain.projects_status import ProjectStatusInfo, ProjectsStatus
from domain.repositories.program_repository import ProgramRepository

class RebuildStatusSummaryUseCase:
    def __init__(self, program_repository: ProgramRepository):
        self.program_repository = program_repository

    async def execute(self):
        projects_data = await self.program_repository.find_projects()

        projects_status = ProjectsStatus()
        for project_data in projects_data:
            projects_status[project_data.project] = ProjectStatusInfo(
                status=project_data.status,
                deadline=project_data.deadline
            )

        await self.program_repository.put_projects_status(projects_status)