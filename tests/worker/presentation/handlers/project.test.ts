import { describe, expect, it, vi } from "vitest";
import { getProject, type GetProjectRouterRequest } from "@worker/presentation/handlers/project";
import type { ProjectService } from "@worker/application/services/project_service";
import { buildProject } from "../../data/builders/project.builder";

const mockProjectService: ProjectService = {
  getProject: vi.fn(async (projectId: string) => {
    if (projectId === 'TSI-061000-2019-0001') {
      return buildProject();
    }
    return null;
  }),
};

describe('Project handler', () => {
  it('should return project', async () => {
    const request = {
      params: {
        id: 'TSI-061000-2019-0001'
      },
    } as GetProjectRouterRequest;

    const response = await getProject(request, mockProjectService);

    expect(response.status).toEqual(200);
    const contentType = response.headers.get('Content-Type');
    expect(contentType).toContain('application/json');
    const cacheControl = response.headers.get('Cache-Control');
    expect(cacheControl).toEqual('public, max-age=86400');
    expect(mockProjectService.getProject).toHaveBeenCalledWith("TSI-061000-2019-0001");
  });

  it('should return 404 when service returns no data', async () => {
    const request = {
      params: {
        id: 'TSI-otherid'
      },
    } as GetProjectRouterRequest;

    const response = await getProject(request, mockProjectService);

    expect(response.status).toEqual(404);
  });
});
