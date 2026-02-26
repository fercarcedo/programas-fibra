export interface ProjectWebResponse {
    status: string;
    eligible_budget: string;
    funding: string;
    subsidy: string | null;
    loan: string | null;
    funding_percentage: string;
    technology: string;
    deadline: string | null;
}

export interface ProjectAwardInfoWebResponse {
    eligible_budget: string;
    funding: string;
    subsidy: string | null;
    loan: string | null;
    funding_percentage: string;
    technology: string;
}