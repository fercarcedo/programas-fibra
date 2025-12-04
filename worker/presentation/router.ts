import { AutoRouter, type IRequest } from 'itty-router';
import { getData, type GetDataRouterRequest } from './handlers/data';
import { getProject, type GetProjectRouterRequest } from './handlers/project';
import { getTile, type GetTileRouterRequest } from './handlers/tile';

const router = AutoRouter();

router.get("/data/:key", async (request: IRequest, _env, _ctx, container) => {
  const geoDataService = container.getGeoDataService();
  const dataRequest = request as GetDataRouterRequest;
  return await getData(dataRequest, geoDataService);
});

router.get("/api/projects/:id", async (request: IRequest, _env, _ctx, container) => {
  const projectService = container.getProjectService();
  const projectRequest = request as GetProjectRouterRequest;
  return await getProject(projectRequest, projectService);
});

router.get("/tiles/:tileName/:z/:x/:y", async (request: IRequest, _env, _ctx, container) => {
  const tileService = container.getTileService();
  const tileRequest = request as GetTileRouterRequest;
  return await getTile(tileRequest, tileService);
});

export default { ...router };