import { describe, expect, it, vi } from "vitest";
import { KVProjectRepository } from "@worker/persistence/repositories/kv_project_repository";
import type { Env } from "@worker/types";
import { buildProjectKV } from "../../data/builders/project_kv.builder";
import { buildProject } from "../../data/builders/project.builder";

const mockEnv: Env = {
  PROJECTS: {
    get: vi.fn(async (key: string) => {
      if (key === "TSI-061000-2019-0001") {
        return JSON.stringify(buildProjectKV());
      }
    }),
  },
};

describe("KV project repository", () => {
  it("should return data", async () => {
    const repository = new KVProjectRepository(mockEnv);
    const project = await repository.getProject("TSI-061000-2019-0001");
    const expectedProject = buildProject();

    expect(project).toEqual(expectedProject);
    expect(mockEnv.PROJECTS.get).toHaveBeenCalledWith("TSI-061000-2019-0001");
  });

  it("should return null when bucket returns no data", async () => {
    const repository = new KVProjectRepository(mockEnv);
    const project = await repository.getProject("TSI-notfound");

    expect(project).toBeNull();
    expect(mockEnv.PROJECTS.get).toHaveBeenCalledWith("TSI-notfound");
  });
});
