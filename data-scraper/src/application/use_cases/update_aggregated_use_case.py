from domain.repositories.program_repository import ProgramRepository


class UpdateAggregatedUseCase:
    def __init__(self, program_repository: ProgramRepository):
        self.program_repository = program_repository

    async def execute(self):
        projects_data = await self.program_repository.find_projects()

        await self.program_repository.put_aggregated(projects_data)

