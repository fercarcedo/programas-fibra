import { ProjectKV } from "@worker/persistence/model/project_kv";

const DEFAULT_PROJECT_KV: ProjectKV = {
    status: 'finished',
    eligible_budget: 125234,
    funding: 75140,
    subsidy: 10269.18,
    loan: 1234,
    funding_percentage: 60,
    technology: "FTTH",
    deadline: new Date("2021-12-31T00:00:00.000Z")
}

export const buildProjectKV = (overrides: Partial<ProjectKV> = {}): ProjectKV => {
  return {
    ...DEFAULT_PROJECT_KV,
    ...overrides,
  };
};