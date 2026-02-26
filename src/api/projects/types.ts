export interface ProjectAward {
  eligible_budget: string;
  funding: string;
  subsidy: string | null;
  loan: string | null;
  funding_percentage: string;
  technology: string;
}

export type ProjectStatus = 'in_progress' | 'finished' | 'cancelled';

export interface ProjectsStatusSummaryInfo {
    status: ProjectStatus;
    deadline: string | null;
}

export interface ProjectsStatusSummary {
  [projectId: string]: ProjectsStatusSummaryInfo;
}