export type AreaType = "town" | "area";

export interface AreaProperties {
  type: AreaType;
  autonomous_community: string;
  province: string;
  project: string;
  grantee: string;
  area_code: string;
  municipality: string;
  program_name: string;
  building_count?: number | undefined;
  house_count?: number | undefined;
  town?: string | undefined;
  exception_zone_code?: string | undefined;
  exception_zone_name?: string | undefined;
}
