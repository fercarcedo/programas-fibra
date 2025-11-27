import type { Project } from "../../application/domain/project";
import type { ProjectRepository } from "../../application/repositories/project_repository";
import type { Env } from '../../types';
import { toDomain } from "../mapper/project_mapper";
import type { ProjectKV } from "../model/project_kv";

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
}