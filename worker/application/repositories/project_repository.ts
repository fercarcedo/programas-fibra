import type { Project } from "../domain/project";

export interface ProjectRepository {
  getProject(projectId: string): Promise<Project | null>;
}