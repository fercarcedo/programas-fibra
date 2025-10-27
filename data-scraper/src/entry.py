from workers import handler
from infrastructure.workflows.workflow import DataScraperWorkflow

@handler
async def on_scheduled(controller, env, ctx):
  instance = await env.WORKFLOW.create()
  print(f"Workflow started: ${instance.id}")