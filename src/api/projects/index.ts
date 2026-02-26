import { useQuery } from "@tanstack/react-query";
import type { ProjectAward, ProjectsStatusSummary } from "./types";

export function useProject(id: string) {
  return useQuery({
    queryKey: [`project${id}`],
    staleTime: 86400 * 1000,
    queryFn: () =>
      fetch(`/api/projects/${id}`).then((res) => res.json()),
  })
}

export function useProjectAward(id: string) {
  return useQuery({
    queryKey: [`projectAward${id}`],
    staleTime: Infinity,
    queryFn: () =>
      fetch(`/api/projects/${id}/award`).then((res) => res.json()) as Promise<ProjectAward>,
  })
}

export function useProjectsStatus() {
  return useQuery({
    queryKey: ['projectsStatus'],
    staleTime: 3600 * 1000,
    queryFn: () =>
      fetch('/api/projects/status').then((res) => res.json()) as Promise<ProjectsStatusSummary>,
  })
}