import { WorkerEntrypoint } from "cloudflare:workers";
import router from './presentation/router';
import { DependencyContainer } from "./dependency_container";
import type { Env } from './types';

export default class extends WorkerEntrypoint<Env> {
  private container = new DependencyContainer(this.env);

  async fetch(request: Request) {
    return await router.fetch(request, 
      this.env,
      this.ctx,
      this.container
    );
  }
}
