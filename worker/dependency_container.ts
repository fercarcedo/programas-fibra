import type { GeoDataRepository } from "./application/repositories/geo_data_repository";
import { GeoDataService } from "./application/services/geo_data_service";
import { R2GeoDataRepository } from "./persistence/repositories/r2_geo_data_repository";
import type { Env } from './types';

export class DependencyContainer {
  private geoDataService: GeoDataService;

  constructor(env: Env) {
    const geoDataRepository: GeoDataRepository = new R2GeoDataRepository(env);
    this.geoDataService = new GeoDataService(geoDataRepository);
  }

  getGeoDataService(): GeoDataService {
    return this.geoDataService;
  }
}