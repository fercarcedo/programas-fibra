from workers import WorkflowEntrypoint
from dataclasses import asdict
from workflow.step.check_updated_programs_step import CheckUpdatedProgramsStep
from workflow.step.process_programs_step import ProcessProgramsStep
from domain.program_update_result import ProgramUpdateResult
from pyodide.ffi import to_js
from js import Object

class DataScraperWorkflow(WorkflowEntrypoint):
    def __init__(self, ctx, env):
        self.check_updated_programs_step = CheckUpdatedProgramsStep(env)
        self.process_programs_step = ProcessProgramsStep(env)
        self.env = env

    async def run(self, event, step):
        program = event["payload"].get("program")

        @step.do('check-updated-programs')
        async def check_updated_programs_step():
            program_update_results = await self.check_updated_programs_step.run()
            return [asdict(program_update_result) for program_update_result in program_update_results]

        @step.do('process-program')
        async def process_program_step():
            return await self.process_programs_step.run(ProgramUpdateResult(**program))

        async def schedule_process_programs(updated_programs_dict):
            updated_programs = [ProgramUpdateResult(**program_dict) for program_dict in updated_programs_dict]
            for i, program in enumerate(updated_programs):
                @step.do(f'schedule-process-program-{program.program_name}')
                async def start_workflow():
                    workflow_options = to_js({"params": { "program": asdict(program) }}, dict_converter=Object.fromEntries)
                    await self.env.WORKFLOW.create(workflow_options)

                await start_workflow()

                if i < len(updated_programs) - 1:
                    await step.sleep(f"delay-{updated_programs[i + 1].program_name}", "1 minute")

        if program is not None:
            await process_program_step()
        else:
            updated_programs = await check_updated_programs_step()
            await schedule_process_programs(updated_programs)