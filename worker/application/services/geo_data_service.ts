import type { GeoDataRepository } from "../repositories/geo_data_repository";

export class GeoDataService {
  private geoDataRepository: GeoDataRepository;
    
  constructor(geoDataRepository: GeoDataRepository) {
    this.geoDataRepository = geoDataRepository;
  }

  async getData(key: string): Promise<ReadableStream | null> {
    if (!key.startsWith('aggregated-')) {
      console.warn(`Attempted access with invalid key format: ${key}`);
      return null;
    }
    return await this.geoDataRepository.getData(key);
  }
}