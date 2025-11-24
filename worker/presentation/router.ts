import { AutoRouter, type IRequest } from 'itty-router';
import { getData, type GetDataRouterRequest } from './handlers/data';

const router = AutoRouter();

router.get("/data/:key", async (request: IRequest, _env, _ctx, container) => {
  const geoDataService = container.getGeoDataService();
  const dataRequest = request as GetDataRouterRequest;
  return getData(dataRequest, geoDataService);
});

router.get("/api/", () => {
  return null;
});

export default { ...router };