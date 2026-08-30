import { describe, expect, it } from "vitest";
import { toDomain } from "@worker/persistence/mapper/project_mapper";
import { ProjectKV } from "@worker/persistence/model/project_kv";
import { Project } from "@worker/application/domain/project";
import { buildProjectKV } from "../../data/builders/project_kv.builder";
import { buildProject } from "../../data/builders/project.builder";

describe("Project mapper", () => {
  it("should map to domain", async () => {
    const projectInfra: ProjectKV = buildProjectKV();
    const expectedProject: Project = buildProject();

    const project = toDomain(projectInfra);
    expect(project).toEqual(expectedProject);
  });

  it("should map to domain with null loan", async () => {
    const projectInfra: ProjectKV = buildProjectKV({ loan: null });
    const expectedProject: Project = buildProject({ loan: null });

    const project = toDomain(projectInfra);
    expect(project).toEqual(expectedProject);
  });

  it("should map to domain with null subsidy", async () => {
    const projectInfra: ProjectKV = buildProjectKV({ subsidy: null });
    const expectedProject: Project = buildProject({ subsidy: null });

    const project = toDomain(projectInfra);
    expect(project).toEqual(expectedProject);
  });
});
