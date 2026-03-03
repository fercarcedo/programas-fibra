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
  getETag: vi.fn(async (key: string) => {
    if (key === 'aggregated-first.json') {
      return '"abc123def456"';
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
      headers: {
        get: vi.fn((name: string) => {
          if (name === 'If-None-Match') {
            return null;
          }
          return null;
        }),
      },
    } as unknown as GetDataRouterRequest;

    const response = await getData(request, mockGeoDataService);

    expect(response.status).toEqual(200);
    const contentType = response.headers.get('Content-Type');
    expect(contentType).toContain('application/json');
    const cacheControl = response.headers.get('Cache-Control');
    expect(cacheControl).toEqual('no-cache');
    const etag = response.headers.get('ETag');
    expect(etag).toEqual('"abc123def456"');
    expect(mockGeoDataService.getData).toHaveBeenCalledWith("aggregated-first.json");
  });

  it('should return 404 when service returns no data', async () => {
    const request = {
      params: {
        key: 'aggregated-notfound.json'
      },
      headers: {
        get: vi.fn(() => {
          return null;
        }),
      },
    } as unknown as GetDataRouterRequest;

    const response = await getData(request, mockGeoDataService);

    expect(response.status).toEqual(404);
  });
});
