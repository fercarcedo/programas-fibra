import type { ProjectStatusKV } from "./project_kv";

export interface ProjectStatusInfoKV {
    status: ProjectStatusKV;
    deadline: string | null;
}

export interface ProjectsStatusInfoKV {
    [projectId: string]: ProjectStatusInfoKV;
}