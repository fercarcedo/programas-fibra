import { useQuery } from "@tanstack/react-query";
import type { ProjectsStatusSummary } from "./types";

export function useProject(id: string) {
  return useQuery({
    queryKey: [`project${id}`],
    staleTime: 86400 * 1000,
    queryFn: () =>
      fetch(`/api/projects/${id}`).then((res) => res.json()),
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