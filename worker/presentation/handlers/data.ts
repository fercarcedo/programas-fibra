import type { IRequest } from "itty-router";
import type { GeoDataService } from "../../application/services/geo_data_service";

export interface GetDataRouterRequest extends IRequest {
  params: {
    key: string;
  };
}

export async function getData(
  request: GetDataRouterRequest,
  geoDataService: GeoDataService,
) {
  const key = request.params.key;
  const object = await geoDataService.getData(key);

  if (!object) {
    console.warn(`Data not found for key: ${key}`);
    return new Response("Not found", { status: 404 });
  }

  const ifNoneMatch = request.headers.get("If-None-Match");
  const etag = await geoDataService.getETag(key);

  if (ifNoneMatch && etag && ifNoneMatch === etag) {
    return new Response(null, { status: 304 });
  }

  return new Response(object, {
    headers: {
      "content-type": "application/json; charset=UTF-8",
      etag: etag!,
      "cache-control": "no-cache",
    },
  });
}
