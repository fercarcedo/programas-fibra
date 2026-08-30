import type { Project, ProjectsStatus } from "../domain/project";

export interface ProjectRepository {
  getProject(projectId: string): Promise<Project | null>;
  getProjectsStatus(): Promise<ProjectsStatus | null>;
  getProjectsStatusLastModified(): Promise<string | null>;
}
