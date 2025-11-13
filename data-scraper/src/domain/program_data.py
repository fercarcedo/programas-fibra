from dataclasses import dataclass
from enum import Enum
from datetime import date

class ProgramStatus(Enum):
    IN_PROGRESS = 0
    FINISHED = 1
    CANCELLED = 2

@dataclass
class ProjectData:
    project: str
    status: ProgramStatus
    eligible_budget: float
    funding: float
    subsidy: float
    loan: float
    funding_percentage: float
    technology: str
    deadline: date
    last_updated: int

    def to_dict(self) -> dict[str, any]:
        return {
            "project": self.project,
            "status": self.status.value,
            "eligible_budget": self.eligible_budget,
            "funding": self.funding,
            "subsidy": self.subsidy,
            "loan": self.loan,
            "funding_percentage": self.funding_percentage,
            "technology": self.technology,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "last_updated": self.last_updated
        }

@dataclass
class ProgramData:
    projects: list[ProjectData]

    def to_dict(self) -> dict[str, any]:
        return {
            "projects": [p.to_dict() for p in self.projects]
        }
