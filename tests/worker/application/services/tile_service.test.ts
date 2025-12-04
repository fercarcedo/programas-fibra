import { beforeEach, describe, expect, it, vi } from "vitest";
import type { TileRepository } from "@worker/application/repositories/tile_repository";
import { TileService } from "@worker/application/services/tile_service";
import { createMockMvtBuffer } from "../../data/builders/tile.builder";

const buffer = createMockMvtBuffer();
const mockStream = new ReadableStream({
  start(controller) {
    controller.enqueue(buffer);
    controller.close();
  }
});

const mockRepository: TileRepository = {
  getTile: vi.fn(async (tileName: string, x: number, y: number, z: number) => {
    if (tileName === 'map-test') {
      return mockStream;
    }
    return null;
  })
}

describe('Tile service', () => {
  beforeEach(() => {
    vi.clearAllMocks(); 
  });

  it('should return data', async () => {
    const service = new TileService(mockRepository);
    const stream = await service.getTile('map-test', 20, 30, 40);

    expect(stream).toBe(mockStream);
    expect(mockRepository.getTile).toHaveBeenCalledWith('map-test', 20, 30, 40);
  });

  it('should return null when repository returns no data', async () => {
    const service = new TileService(mockRepository);
    const project = await service.getTile('map-other', 20, 30, 40);

    expect(project).toBeNull();
    expect(mockRepository.getTile).toHaveBeenCalledWith('map-other', 20, 30, 40);
  });
});
