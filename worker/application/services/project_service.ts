import type { Project, ProjectsStatus } from "../domain/project";
import type { ProjectRepository } from "../repositories/project_repository";

export class ProjectService {
  private projectRepository: ProjectRepository;

  constructor(projectRepository: ProjectRepository) {
    this.projectRepository = projectRepository;
  }

  private normalizeProjectCode(projectId: string): string | null {
    // Normalize by removing leading zeros from the numeric suffix
    // TSI-061000-2015-0114 -> TSI-061000-2015-114
    const parts = projectId.split("-");
    if (parts.length === 4 && parts[0] === "TSI") {
      const suffix = parts[3];
      if (/^\d+$/.test(suffix)) {
        const normalized = String(parseInt(suffix, 10));
        if (normalized !== suffix) {
          return `${parts[0]}-${parts[1]}-${parts[2]}-${normalized}`;
        }
      }
    }
    return null;
  }

  async getProject(projectId: string): Promise<Project | null> {
    if (!projectId.startsWith("TSI-")) {
      console.warn(`Invalid project id: ${projectId}`);
      return null;
    }

    let project = await this.projectRepository.getProject(projectId);

    if (!project) {
      const normalized = this.normalizeProjectCode(projectId);
      if (normalized) {
        project = await this.projectRepository.getProject(normalized);
        if (project) {
          console.info(
            `Found project using normalized id: ${projectId} -> ${normalized}`,
          );
        }
      }
    }

    return project;
  }

  async getProjectsStatus(): Promise<ProjectsStatus | null> {
    return await this.projectRepository.getProjectsStatus();
  }

  async getProjectsStatusLastModified(): Promise<string | null> {
    return await this.projectRepository.getProjectsStatusLastModified();
  }
}
