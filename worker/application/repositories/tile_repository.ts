export interface TileRepository {
  getTile(
    tileName: string, 
    x: number, 
    y: number, 
    z: number
  ): Promise<ReadableStream | null>;
}