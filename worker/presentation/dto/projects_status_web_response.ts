export interface ProjectsStatusInfoWebResponse {
  status: string;
  deadline: string | null;
}

export interface ProjectsStatusWebResponse {
  [projectId: string]: ProjectsStatusInfoWebResponse;
}
