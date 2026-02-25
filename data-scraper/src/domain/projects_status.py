from dataclasses import dataclass
from datetime import date
from domain.program_data import ProgramStatus

@dataclass
class ProjectStatusInfo:
    status: ProgramStatus
    deadline: date

ProjectsStatus = dict[str, ProjectStatusInfo]