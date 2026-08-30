import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectRepository } from "@worker/application/repositories/project_repository";
import { ProjectService } from "@worker/application/services/project_service";
import { buildProject } from "../../data/builders/project.builder";

const mockRepository: ProjectRepository = {
  getProject: vi.fn(async (key: string) => {
    if (key === "TSI-061000-2019-0001") {
      return buildProject();
    }
    if (key === "TSI-061000-2015-114") {
      return buildProject();
    }
    return null;
  }),
};

describe("Project service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return data", async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject("TSI-061000-2019-0001");
    const expectedProject = buildProject();

    expect(project).toEqual(expectedProject);
    expect(mockRepository.getProject).toHaveBeenCalledWith(
      "TSI-061000-2019-0001",
    );
  });

  it("should return null when repository returns no data", async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject("TSI-notfound");

    expect(project).toBeNull();
    expect(mockRepository.getProject).toHaveBeenCalledWith("TSI-notfound");
  });

  it("should return null if project id does not start with TSI-", async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject("other");

    expect(project).toBeNull();
    expect(mockRepository.getProject).not.toHaveBeenCalled();
  });

  it("should normalize project code with leading zeros if original not found", async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject("TSI-061000-2015-0114");
    const expectedProject = buildProject();

    expect(project).toEqual(expectedProject);
    // Should first try the original, then the normalized
    expect(mockRepository.getProject).toHaveBeenCalledTimes(2);
    expect(mockRepository.getProject).toHaveBeenNthCalledWith(
      1,
      "TSI-061000-2015-0114",
    );
    expect(mockRepository.getProject).toHaveBeenNthCalledWith(
      2,
      "TSI-061000-2015-114",
    );
  });

  it("should use original if it exists in repository", async () => {
    const service = new ProjectService(mockRepository);
    const project = await service.getProject("TSI-061000-2019-0001");
    const expectedProject = buildProject();

    expect(project).toEqual(expectedProject);
    // Should only call once since original exists
    expect(mockRepository.getProject).toHaveBeenCalledTimes(1);
    expect(mockRepository.getProject).toHaveBeenCalledWith(
      "TSI-061000-2019-0001",
    );
  });
});
