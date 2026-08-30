import { AutoRouter, type IRequest } from "itty-router";
import { getData, type GetDataRouterRequest } from "./handlers/data";
import {
  ProjectHandler,
  type GetProjectRouterRequest,
} from "./handlers/project";

const router = AutoRouter();

const projectHandler = new ProjectHandler();

router.get("/data/:key", async (request: IRequest, _env, _ctx, container) => {
  const geoDataService = container.getGeoDataService();
  const dataRequest = request as GetDataRouterRequest;
  return await getData(dataRequest, geoDataService);
});

router.get(
  "/api/projects/status",
  async (request: IRequest, _env, _ctx, container) => {
    const projectService = container.getProjectService();
    return await projectHandler.getProjectsStatus(request, projectService);
  },
);

router.get(
  "/api/projects/:id",
  async (request: IRequest, _env, _ctx, container) => {
    const projectService = container.getProjectService();
    const projectRequest = request as GetProjectRouterRequest;
    return await projectHandler.getProject(projectRequest, projectService);
  },
);

router.get(
  "/api/projects/:id/award",
  async (request: IRequest, _env, _ctx, container) => {
    const projectService = container.getProjectService();
    return await projectHandler.getProjectAwardInfo(request, projectService);
  },
);

export default { ...router };
