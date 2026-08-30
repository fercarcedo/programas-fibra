import type { GeoDataRepository } from "../repositories/geo_data_repository";

const ALLOWED_GEO_RESOURCES = ["aggregated"];

export class GeoDataService {
  private geoDataRepository: GeoDataRepository;

  constructor(geoDataRepository: GeoDataRepository) {
    this.geoDataRepository = geoDataRepository;
  }

  private isAllowedResource(key: string): boolean {
    return ALLOWED_GEO_RESOURCES.some((resource) => key.startsWith(resource));
  }

  async getData(key: string): Promise<ReadableStream | null> {
    if (!this.isAllowedResource(key)) {
      console.warn(`Attempted access with invalid key format: ${key}`);
      return null;
    }
    return await this.geoDataRepository.getData(key);
  }

  async getETag(key: string): Promise<string | null> {
    if (!this.isAllowedResource(key)) {
      console.warn(`Attempted access with invalid key format: ${key}`);
      return null;
    }
    return await this.geoDataRepository.getETag(key);
  }
}
