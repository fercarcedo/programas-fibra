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
    erdf_advance_payment: float
    funding_percentage: float
    technology: str
    deadline: date
    last_updated: int

@dataclass
class ProgramData:
    projects: list[ProjectData]