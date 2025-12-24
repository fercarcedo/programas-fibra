import type { IRequest } from "itty-router";
import type { ProjectService } from "../../application/services/project_service";
import { toWebResponse } from "../mapper/project_mapper";

export interface GetProjectRouterRequest extends IRequest {
  params: {
    id: string;
  };
}

export async function getProject(request: GetProjectRouterRequest, projectService: ProjectService) {
  const projectId = request.params.id;
  const project = await projectService.getProject(projectId);

  if (!project) {
    console.warn(`Project info not found for id: ${projectId}`);
    return new Response('Not found', { status: 404 });
  }

  const projectResponse = toWebResponse(project);
  return new Response(JSON.stringify(projectResponse), {
    headers: {
      'content-type': 'application/json; charset=UTF-8',
      'cache-control': 'public, max-age=86400',
    },
  });
}