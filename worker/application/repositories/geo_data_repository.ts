export interface GeoDataRepository {
  getData(key: string): Promise<ReadableStream | null>;
}