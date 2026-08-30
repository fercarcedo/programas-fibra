import type { Project } from "../../application/domain/project";
import type { ProjectKV } from "../model/project_kv";

export function toDomain(infra: ProjectKV): Project {
  return {
    status: infra.status,
    eligible_budget: infra.eligible_budget,
    funding: infra.funding,
    subsidy: infra.subsidy,
    loan: infra.loan,
    funding_percentage: infra.funding_percentage,
    technology: infra.technology,
    deadline: infra.deadline ? new Date(infra.deadline) : null,
  };
}
