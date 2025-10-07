from workers import WorkerEntrypoint

class Default(WorkerEntrypoint):

    async def scheduled(self, controller, env, ctx):
      print("cron processed")

      # Optional: Use ctx.waitUntil if you have async tasks
      # that need to finish before the Worker is terminated.
      # ctx.waitUntil(some_async_task())