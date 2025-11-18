from dataclasses import dataclass
from enum import Enum
from datetime import date

class ProgramStatus(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"

@dataclass
class ProjectEntity:
    status: ProgramStatus
    eligible_budget: float
    funding: float
    subsidy: float
    loan: float
    funding_percentage: float
    technology: str
    deadline: date

    def to_dict(self) -> dict[str, any]:
        return {
            "status": self.status.value,
            "eligible_budget": self.eligible_budget,
            "funding": self.funding,
            "subsidy": self.subsidy,
            "loan": self.loan,
            "funding_percentage": self.funding_percentage,
            "technology": self.technology,
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }