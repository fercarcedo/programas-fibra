from workers import WorkerEntrypoint
from workflow.workflow import DataScraperWorkflow

class Default(WorkerEntrypoint):

    async def scheduled(self, *_):
      instance = await self.env.WORKFLOW.create()
      print(f"Workflow started: ${instance['id']}")