export interface GeoDataRepository {
  getData(key: string): Promise<ReadableStream | null>;
  getETag(key: string): Promise<string | null>;
}
