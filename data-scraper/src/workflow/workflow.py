from workers import WorkflowEntrypoint

class DataScraperWorkflow(WorkflowEntrypoint):
    async def run(self, event, step):
        @step.do('step-name')
        async def first_step():
            return "Hello, World!"

        await first_step()