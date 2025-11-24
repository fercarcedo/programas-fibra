import { describe, expect, it, vi } from "vitest";
import { getData, type GetDataRouterRequest } from "@worker/presentation/handlers/data";
import type { GeoDataService } from "@worker/application/services/geo_data_service";

const mockGeoDataService: GeoDataService = {
  getData: vi.fn(async (key: string) => {
    if (key === 'aggregated-first.json') {
      return { data: 'test-data' };
    }
    return null;
  }),
};

describe('Data handler', () => {
  it('should return data', async () => {
    const request = {
      params: {
        key: 'aggregated-first.json'
      },
    } as GetDataRouterRequest;

    const response = await getData(request, mockGeoDataService);

    expect(response.status).toEqual(200);
    const contentType = response.headers.get('Content-Type');
    expect(contentType).toContain('application/json');
    const cacheControl = response.headers.get('Cache-Control');
    expect(cacheControl).toEqual('public, max-age=31536000, immutable');
    expect(mockGeoDataService.getData).toHaveBeenCalledWith("aggregated-first.json");
  });

  it('should return 404 when service returns no data', async () => {
    const request = {
      params: {
        key: 'aggregated-notfound.json'
      },
    } as GetDataRouterRequest;

    const response = await getData(request, mockGeoDataService);

    expect(response.status).toEqual(404);
  });
});
