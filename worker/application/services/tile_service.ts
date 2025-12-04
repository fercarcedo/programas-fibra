import type { TileRepository } from "../repositories/tile_repository";

export class TileService {
  private tileRepository: TileRepository;
    
  constructor(tileRepository: TileRepository) {
    this.tileRepository = tileRepository;
  }

  async getTile(
    tileName: string, 
    x: number, 
    y: number, 
    z: number
  ): Promise<ReadableStream | null> {
    return await this.tileRepository.getTile(tileName, x, y, z);
  }
}