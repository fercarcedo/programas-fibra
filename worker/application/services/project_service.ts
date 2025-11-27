import type { Project } from "../domain/project";
import type { ProjectRepository } from "../repositories/project_repository";

export class ProjectService {
  private projectRepository: ProjectRepository;
    
  constructor(projectRepository: ProjectRepository) {
    this.projectRepository = projectRepository;
  }

  async getProject(projectId: string): Promise<Project | null> {
    if (!projectId.startsWith('TSI-')) {
      console.warn(`Invalid project id: ${projectId}`);
      return null;
    }
    return await this.projectRepository.getProject(projectId);
  }
}