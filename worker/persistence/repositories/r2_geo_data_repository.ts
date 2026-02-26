import type { GeoDataRepository } from "../../application/repositories/geo_data_repository";
import type { Env } from '../../types';

export class R2GeoDataRepository implements GeoDataRepository {
  private env: Env;

  constructor(env: Env) {
    this.env = env;
  }

  async getData(key: string): Promise<ReadableStream | null> {
    const object = await this.env.BUCKET_GEO.get(key);
    if (object == null) {
      return null;
    }
    return object.body;
  }

  async getETag(key: string): Promise<string | null> {
    const headResponse = await this.env.BUCKET_GEO.head(key);
    if (headResponse == null) {
      return null;
    }
    return headResponse.httpEtag;
  }
}