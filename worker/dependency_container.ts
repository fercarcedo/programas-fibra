import type { GeoDataRepository } from "./application/repositories/geo_data_repository";
import type { ProjectRepository } from "./application/repositories/project_repository";
import type { TileRepository } from "./application/repositories/tile_repository";
import { GeoDataService } from "./application/services/geo_data_service";
import { ProjectService } from "./application/services/project_service";
import { TileService } from "./application/services/tile_service";
import { KVProjectRepository } from "./persistence/repositories/kv_project_repository";
import { R2GeoDataRepository } from "./persistence/repositories/r2_geo_data_repository";
import { WorkerTileRepository } from "./persistence/repositories/worker_tile_repository";
import type { Env } from './types';

export class DependencyContainer {
  private geoDataService: GeoDataService;
  private projectService: ProjectService;
  private tileService: TileService;

  constructor(env: Env) {
    const geoDataRepository: GeoDataRepository = new R2GeoDataRepository(env);
    this.geoDataService = new GeoDataService(geoDataRepository);
    const projectRepository: ProjectRepository = new KVProjectRepository(env);
    this.projectService = new ProjectService(projectRepository);
    const tileRepository: TileRepository = new WorkerTileRepository(env);
    this.tileService = new TileService(tileRepository);
  }

  getGeoDataService(): GeoDataService {
    return this.geoDataService;
  }

  getProjectService(): ProjectService {
    return this.projectService;
  }

  getTileService(): TileService {
    return this.tileService;
  }
}