export type ProjectStatusKV =
    | 'cancelled'
    | 'in_progress'
    | 'finished';

export interface ProjectKV {
    status: ProjectStatusKV;
    eligible_budget: number;
    funding: number;
    subsidy: number | null;
    loan: number | null;
    funding_percentage: number;
    technology: string;
    deadline: string | null;
}