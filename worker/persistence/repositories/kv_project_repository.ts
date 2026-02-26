import type { Project, ProjectsStatus } from "../../application/domain/project";
import type { ProjectRepository } from "../../application/repositories/project_repository";
import type { Env } from '../../types';
import { toDomain } from "../mapper/project_mapper";
import { toDomain as toProjectStatusInfoDomain } from "../mapper/project_status_mapper";
import type { ProjectKV } from "../model/project_kv";
import { ProjectStatusInfoKV, type ProjectsStatusInfoKV, type ProjectStatusInfoKVMetadata } from "../model/project_status_kv";

export class KVProjectRepository implements ProjectRepository {
  private env: Env;

  constructor(env: Env) {
    this.env = env;
  }

  async getProject(projectId: string): Promise<Project | null> {
    const projectJSON = await this.env.PROJECTS.get(projectId);
    if (projectJSON == null) {
      return null;
    }

    const project: ProjectKV = JSON.parse(projectJSON);
    return toDomain(project);
  }

  async getProjectsStatus(): Promise<ProjectsStatus | null> {
    const statusData = await this.env.PROJECTS.get<ProjectsStatusInfoKV>("projects-status", "json");
    if (!statusData) {
      return null;
    }

    return toProjectStatusInfoDomain(statusData);
  }

  async getProjectsStatusLastModified(): Promise<string | null> {
    return await this.env.PROJECTS.get("projects-status:last-modified");
  }
}