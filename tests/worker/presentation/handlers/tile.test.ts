import { describe, expect, it, vi } from "vitest";
import { getTile, type GetTileRouterRequest } from "@worker/presentation/handlers/tile";
import type { TileService } from "@worker/application/services/tile_service";
import { createMockMvtBuffer } from "../../data/builders/tile.builder";

const mockTileService: TileService = {
  getTile: vi.fn(async (tileName: string, x: number, y: number, z: number) => {
    if (tileName === 'map-test') {
        return createMockMvtBuffer();
    }
    return null;
  }),
};

describe('Tile handler', () => {
  it('should return tile', async () => {
    const request = {
      params: {
        tileName: 'map-test',
        x: 20,
        y: 30,
        z: 40
      },
    } as GetTileRouterRequest;

    const response = await getTile(request, mockTileService);

    expect(response.status).toEqual(200);
    const contentType = response.headers.get('Content-Type');
    expect(contentType).toContain('application/x-protobuf');
    const cacheControl = response.headers.get('Cache-Control');
    expect(cacheControl).toEqual('public, max-age=31536000, immutable');
    expect(mockTileService.getTile).toHaveBeenCalledWith("map-test", 20, 30, 40);
    const text = await response.text();
    expect(text.length).toBeGreaterThan(0);
  });

  it('should return 200 with empty response when service returns no data', async () => {
    const request = {
      params: {
        tileName: 'map-other',
        x: 20,
        y: 30,
        z: 40
      },
    } as GetTileRouterRequest;

    const response = await getTile(request, mockTileService);

    expect(response.status).toEqual(200);
    const text = await response.text();
    expect(text.length).toBe(0);
    const contentType = response.headers.get('Content-Type');
    expect(contentType).toContain('application/x-protobuf');
    const cacheControl = response.headers.get('Cache-Control');
    expect(cacheControl).toEqual('public, max-age=3600');
  });

  it('should return 400 if tile x is not a number', async () => {
    const request = {
      params: {
        tileName: 'map-other',
        x: 'other',
        y: 30,
        z: 40
      },
    } as GetTileRouterRequest;

    const response = await getTile(request, mockTileService);

    expect(response.status).toEqual(400);
  });

  it('should return 400 if tile y is not a number', async () => {
    const request = {
      params: {
        tileName: 'map-other',
        x: 20,
        y: 'other',
        z: 40
      },
    } as GetTileRouterRequest;

    const response = await getTile(request, mockTileService);

    expect(response.status).toEqual(400);
  });

  it('should return 400 if tile z is not a number', async () => {
    const request = {
      params: {
        tileName: 'map-other',
        x: 20,
        y: 30,
        z: 'other'
      },
    } as GetTileRouterRequest;

    const response = await getTile(request, mockTileService);

    expect(response.status).toEqual(400);
  });
});
