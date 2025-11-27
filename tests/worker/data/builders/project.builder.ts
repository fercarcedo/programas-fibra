import { Project } from "@worker/application/domain/project";

const DEFAULT_PROJECT: Project = {
    status: 'finished',
    eligible_budget: 125234,
    funding: 75140,
    subsidy: 10269.18,
    loan: 1234,
    funding_percentage: 60,
    technology: "FTTH",
    deadline: new Date("2021-12-31T00:00:00.000Z")
}

export const buildProject = (overrides: Partial<Project> = {}): Project => {
  return {
    ...DEFAULT_PROJECT,
    ...overrides,
  };
};