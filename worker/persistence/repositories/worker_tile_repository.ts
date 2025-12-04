import type { TileRepository } from "../../application/repositories/tile_repository";
import type { Env } from '../../types';

export class WorkerTileRepository implements TileRepository {
  private env: Env;

  constructor(env: Env) {
    this.env = env;
  }
    
  async getTile(
    tileName: string, 
    x: number, 
    y: number, 
    z: number
  ): Promise<ReadableStream | null> {
    const response = await this.env.TILE_WORKER.fetch(`https://tile-server/${tileName}/${z}/${x}/${y}.mvt`);

    if (!response.ok) {
        return null;
    }
    
    return response.body!;
  }
}