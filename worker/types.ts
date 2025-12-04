export interface Env {
  BUCKET_GEO: R2Bucket;
  PROJECTS: KVNamespace;
  TILE_WORKER: Fetcher;
}
