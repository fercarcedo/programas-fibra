export interface ProjectAward {
  eligible_budget: string;
  funding: string;
  subsidy: string | null;
  loan: string | null;
  funding_percentage: string;
  technology: string;
}

export interface ProjectsStatusSummaryInfo {
    status: string;
    deadline: string | null;
}

export interface ProjectsStatusSummary {
  [projectId: string]: ProjectsStatusSummaryInfo;
}