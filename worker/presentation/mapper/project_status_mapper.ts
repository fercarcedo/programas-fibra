import type {
  ProjectsStatus,
  ProjectStatusInfo,
} from "../../application/domain/project";
import type {
  ProjectsStatusInfoWebResponse,
  ProjectsStatusWebResponse,
} from "../dto/projects_status_web_response";
import { mapDeadline } from "./project_mapper";

function toProjectStatusInfoWebResponse(
  info: ProjectStatusInfo,
): ProjectsStatusInfoWebResponse {
  return {
    status: info.status,
    deadline: mapDeadline(info.deadline),
  };
}

export function toWebResponse(
  projectsStatus: ProjectsStatus,
): ProjectsStatusWebResponse {
  return Object.entries(projectsStatus).reduce((acc, [id, info]) => {
    acc[id] = toProjectStatusInfoWebResponse(info);
    return acc;
  }, {} as ProjectsStatusWebResponse);
}
