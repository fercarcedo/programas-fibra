import type { Project } from "../../application/domain/project";
import type {
  ProjectAwardInfoWebResponse,
  ProjectWebResponse,
} from "../dto/project_web_response";

const euroFormat = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
});

const dateFormat = new Intl.DateTimeFormat("es-ES", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export function toWebResponse(project: Project): ProjectWebResponse {
  return {
    status: project.status,
    eligible_budget: euroFormat.format(project.eligible_budget),
    funding: euroFormat.format(project.funding),
    subsidy: project.subsidy ? euroFormat.format(project.subsidy) : null,
    loan: project.loan ? euroFormat.format(project.loan) : null,
    funding_percentage: `${project.funding_percentage}%`,
    technology: project.technology,
    deadline: mapDeadline(project.deadline),
  };
}

export function toProjectAwardInfoWebResponse(
  project: Project,
): ProjectAwardInfoWebResponse {
  return {
    eligible_budget: euroFormat.format(project.eligible_budget),
    funding: euroFormat.format(project.funding),
    subsidy: project.subsidy ? euroFormat.format(project.subsidy) : null,
    loan: project.loan ? euroFormat.format(project.loan) : null,
    funding_percentage: `${project.funding_percentage}%`,
    technology: project.technology,
  };
}

export function mapDeadline(deadline: Date | null): string | null {
  return deadline ? dateFormat.format(new Date(deadline)) : null;
}
