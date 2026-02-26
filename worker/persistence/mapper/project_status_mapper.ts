import type { ProjectsStatus, ProjectStatusInfo } from "../../application/domain/project";
import type { ProjectsStatusInfoKV, ProjectStatusInfoKV } from "../model/project_status_kv";

function toProjectStatusInfo(kv: ProjectStatusInfoKV): import("../../application/domain/project").ProjectStatusInfo {
    return {
        status: kv.status as ProjectStatusInfo['status'],
        deadline: kv.deadline ? new Date(kv.deadline) : null,
    };
}

export function toDomain(kv: ProjectsStatusInfoKV): ProjectsStatus {
    return Object.entries(kv).reduce((acc, [id, info]) => {
        acc[id] = toProjectStatusInfo(info);
        return acc;
    }, {} as ProjectsStatus);
}