export type ProjectStatus = "cancelled" | "in_progress" | "finished";

export interface Project {
  status: ProjectStatus;
  eligible_budget: number;
  funding: number;
  subsidy: number | null;
  loan: number | null;
  funding_percentage: number;
  technology: string;
  deadline: Date | null;
}

export interface ProjectStatusInfo {
  status: ProjectStatus;
  deadline: Date | null;
}

export interface ProjectsStatus {
  [projectId: string]: ProjectStatusInfo;
}
