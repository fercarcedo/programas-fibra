import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectRepository } from "@worker/application/repositories/project_repository";
import { ProjectService } from "@worker/application/services/project_service";
import { buildProject } from "../../data/builders/project.builder";

const mockRepository: ProjectRepository = {
  getProject: vi.fn(async (key: string) => {
    if (key === 'TSI-061000-2019-0001') {
      return buildProject();
    }
    return null;
  })
}

describe('Project service', () => {
  beforeEach(() => {
    vi.clearAllMocks(); 
  });

  it('should return data', async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject('TSI-061000-2019-0001');
    const expectedProject = buildProject();

    expect(project).toEqual(expectedProject);
    expect(mockRepository.getProject).toHaveBeenCalledWith('TSI-061000-2019-0001');
  });

  it('should return null when repository returns no data', async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject('TSI-notfound');

    expect(project).toBeNull();
    expect(mockRepository.getProject).toHaveBeenCalledWith('TSI-notfound');
  });

  it('should return null if project id does not start with TSI-', async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject('other');

    expect(project).toBeNull();
    expect(mockRepository.getProject).not.toHaveBeenCalled();
  });
});
