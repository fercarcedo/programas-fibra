import { describe, expect, it, vi } from "vitest";
import { R2GeoDataRepository } from "@worker/persistence/repositories/r2_geo_data_repository";
import type { Env } from "@worker/types";
import type { R2ObjectBody } from '@cloudflare/workers-types';

const mockEnv: Env = {
  BUCKET_GEO: {
    get: vi.fn(async (key: string) => {
      if (key === 'aggregated-first.json') {
        return createJsonMock({ data: 'test-data' });
      }
    })
  }
}

async function consumeStream<T>(jsonStream: ReadableStream<T>): T {
  const response = new Response(jsonStream);
  return await response.json();
}

function createJsonMock<T>(data: T): R2ObjectBody {
  const payloadString = JSON.stringify(data);
  const payloadBytes = new TextEncoder().encode(payloadString);

  const mockStream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(payloadBytes);
      controller.close();
    },
  });

  return {
    async json() {
      return data;
    },
    text: vi.fn(() => Promise.resolve(JSON.stringify(data))),
    arrayBuffer: vi.fn(),
    body: mockStream,
    bodyUsed: false,
    key: 'test-key',
    version: 'v1',
    size: 100,
    etag: 'etag',
    httpEtag: 'http-etag',
    uploaded: new Date(),
    customMetadata: {},
    httpMetadata: { contentType: 'application/json' },
    checksums: {},
    writeHttpMetadata: vi.fn(),
  } as R2ObjectBody;
}

describe('R2 geo data repository', () => {
  it('should return data', async () => {
    const repository = new R2GeoDataRepository(mockEnv);
    const stream = await repository.getData('aggregated-first.json');

    expect(await consumeStream(stream)).toEqual({
        data: 'test-data'
    });
    expect(mockEnv.BUCKET_GEO.get).toHaveBeenCalledWith('aggregated-first.json');
  });

  it('should return null when bucket returns no data', async () => {
    const repository = new R2GeoDataRepository(mockEnv);
    const stream = await repository.getData('aggregated-notfound.json');

    expect(stream).toBeNull();
    expect(mockEnv.BUCKET_GEO.get).toHaveBeenCalledWith('aggregated-first.json');
  });
});
