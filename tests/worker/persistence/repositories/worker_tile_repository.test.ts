import { describe, expect, it, vi } from "vitest";
import { WorkerTileRepository } from "@worker/persistence/repositories/worker_tile_repository";
import type { Env } from "@worker/types";
import { createMockMvtBuffer } from "../../data/builders/tile.builder";

const buffer = createMockMvtBuffer();
const mockStream = new ReadableStream({
  start(controller) {
    controller.enqueue(buffer);
    controller.close();
  }
});

const mockEnv: Env = {
  TILE_WORKER: {
    fetch: vi.fn(async (url: string) => {
      if (!url.includes("map-test")) {
        return new Response(null, { status: 404 });
      }
      return new Response(mockStream, { status: 200 });
    })
  }
}

describe('Worker tile repository', () => {
  it('should return data', async () => {
    const repository = new WorkerTileRepository(mockEnv);
    const stream = await repository.getTile('map-test', 20, 30, 40);

    expect(stream).toBe(mockStream);
    expect(mockEnv.TILE_WORKER.fetch).toHaveBeenCalledWith('https://tile-server/map-test/40/20/30.mvt');
  });

  it('should return null when fetch returns no data', async () => {
    const repository = new WorkerTileRepository(mockEnv);
    const stream = await repository.getTile('other-map', 20, 30, 40);

    expect(stream).toBeNull();
    expect(mockEnv.TILE_WORKER.fetch).toHaveBeenCalledWith('https://tile-server/other-map/40/20/30.mvt');
  });
});
