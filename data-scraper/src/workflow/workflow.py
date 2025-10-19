from workers import WorkflowEntrypoint, fetch, Request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
from workflow.step.check_updated_programs_step import CheckUpdatedProgramsStep

class DataScraperWorkflow(WorkflowEntrypoint):
    def __init__(self, ctx, env):
        self.check_updated_programs_step = CheckUpdatedProgramsStep(env)

    async def run(self, event, step):
        @step.do('check-updated-programs')
        async def first_step():
            await self.check_updated_programs_step.run()

        await first_step()