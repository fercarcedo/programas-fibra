from workers import WorkflowEntrypoint, fetch, Request
from dataclasses import asdict
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
        async def check_updated_programs_step():
            program_update_results = await self.check_updated_programs_step.run()
            return [asdict(program_update_result) for program_update_result in program_update_results]

        @step.do('process-programs', depends=[check_updated_programs_step])
        async def process_programs_step(updated_programs):
            pass

        await check_updated_programs_step()