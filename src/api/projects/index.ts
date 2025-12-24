import { useQuery } from "@tanstack/react-query";

export function useProject(id: string) {
  return useQuery({
    queryKey: [`project${id}`],
    staleTime: 86400 * 1000,
    queryFn: () => 
      fetch(`/api/projects/${id}`).then((res) => res.json()),
  })
}