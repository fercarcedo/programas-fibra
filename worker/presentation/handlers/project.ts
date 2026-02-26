import type { IRequest } from "itty-router";
import type { ProjectService } from "../../application/services/project_service";
import { toProjectAwardInfoWebResponse, toWebResponse as toProjectWebResponse } from "../mapper/project_mapper";
import { toWebResponse as toProjectsStatusWebResponse } from "../mapper/project_status_mapper";

export interface GetProjectRouterRequest extends IRequest {
  params: {
    id: string;
  };
}

export class ProjectHandler {
  async getProject(request: GetProjectRouterRequest, projectService: ProjectService) {
    const projectId = request.params.id;
    const project = await projectService.getProject(projectId);

    if (!project) {
      console.warn(`Project info not found for id: ${projectId}`);
      return new Response('Not found', { status: 404 });
    }

    const projectResponse = toProjectWebResponse(project);
    return new Response(JSON.stringify(projectResponse), {
      headers: {
        'content-type': 'application/json; charset=UTF-8',
        'cache-control': 'public, max-age=86400',
      },
    });
  }

  async getProjectAwardInfo(request: IRequest, projectService: ProjectService) {
    const projectId = request.params.id;
    const project = await projectService.getProject(projectId);

    if (!project) {
      console.warn(`Project info not found for id: ${projectId}`);
      return new Response('Not found', { status: 404 });
    }

    const projectAwardInfoResponse = toProjectAwardInfoWebResponse(project);
    return new Response(JSON.stringify(projectAwardInfoResponse), {
      headers: {
        'content-type': 'application/json; charset=UTF-8',
        'cache-control': 'public, max-age=31536000, immutable',
      },
    });
  }

  async getProjectsStatus(request: IRequest, projectService: ProjectService) {
    const ifModifiedSince = request.headers.get("If-Modified-Since");
    const lastModified = await projectService.getProjectsStatusLastModified();

    if (ifModifiedSince && lastModified === ifModifiedSince) {
      return new Response(null, { status: 304 });
    }

    const projectsStatus = await projectService.getProjectsStatus();

    if (!projectsStatus) {
      console.warn("Projects status info not found");
      return new Response('Not found', { status: 404 });
    }

    const projectsWebResponse = toProjectsStatusWebResponse(projectsStatus);
    return new Response(JSON.stringify(projectsWebResponse), {
      headers: {
        'content-type': 'application/json; charset=UTF-8',
        "last-modified": lastModified || new Date().toUTCString(),
        'cache-control': 'no-cache',
      },
    });
  }
}