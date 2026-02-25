from dataclasses import dataclass
from enum import Enum
from datetime import date
from infrastructure.entity.project_entity import ProgramStatus

class ProgramStatusEntity(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"

@dataclass
class ProjectStatusInfoEntity:
    status: ProgramStatusEntity
    deadline: date

    def to_dict(self) -> dict[str, any]:
        return {
            "status": self.status.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }

ProjectsStatusEntity = dict[str, ProjectStatusInfoEntity]

def projects_status_to_dict(entity: ProjectsStatusEntity) -> dict[str, any]:
    return {
        id: info.to_dict()
        for id, info in entity.items()
    }