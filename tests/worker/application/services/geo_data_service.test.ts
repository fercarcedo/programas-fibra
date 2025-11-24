import { beforeEach, describe, expect, it, vi } from "vitest";
import type { GeoDataRepository } from "@worker/application/repositories/geo_data_repository";
import { GeoDataService } from "@worker/application/services/geo_data_service";

const mockRepository: GeoDataRepository = {
  getData: vi.fn(async (key: string) => {
    if (key === 'aggregated-first.json') {
      return createStream({ data: 'test-data' }); 
    }
    return null;
  })
}

async function consumeStream<T>(jsonStream: ReadableStream<T>): T {
  const response = new Response(jsonStream);
  return await response.json();
}

function createStream<T>(data: T): ReadableStream<Uint8Array> {
  const payloadString = JSON.stringify(data);
  const payloadBytes = new TextEncoder().encode(payloadString);

  return new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(payloadBytes);
      controller.close();
    },
  });
}

describe('Geo data service', () => {
  beforeEach(() => {
    vi.clearAllMocks(); 
  });

  it('should return data', async () => {
    const service = new GeoDataService(mockRepository);
    const stream = await service.getData('aggregated-first.json');

    expect(await consumeStream(stream)).toEqual({
        data: 'test-data'
    });
    expect(mockRepository.getData).toHaveBeenCalledWith('aggregated-first.json');
  });

  it('should return null when repository returns no data', async () => {
    const service = new GeoDataService(mockRepository);
    const stream = await service.getData('aggregated-notfound.json');

    expect(stream).toBeNull();
    expect(mockRepository.getData).toHaveBeenCalledWith('aggregated-notfound.json');
  });

  it('should return null if key does not start with aggregated-', async () => {
    const service = new GeoDataService(mockRepository);
    const stream = await service.getData('other.json');

    expect(stream).toBeNull();
    expect(mockRepository.getData).not.toHaveBeenCalled();
  });
});
