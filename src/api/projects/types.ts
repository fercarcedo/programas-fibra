export interface ProjectsStatusSummaryInfo {
    status: string;
    deadline: string | null;
}

export interface ProjectsStatusSummary {
  [projectId: string]: ProjectsStatusSummaryInfo;
}