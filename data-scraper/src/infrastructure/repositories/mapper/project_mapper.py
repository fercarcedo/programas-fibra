from datetime import date

from domain.program_data import ProjectData, ProgramStatus
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus as ProgramStatusEntity

def to_entity(project: ProjectData) -> ProjectEntity:
    return ProjectEntity(
        status=ProgramStatusEntity[project.status.name.upper()],
        eligible_budget=project.eligible_budget,
        funding=project.funding,
        subsidy=project.subsidy,
        loan=project.loan,
        funding_percentage=project.funding_percentage,
        technology=project.technology,
        deadline=project.deadline
    )

def from_entity(entity: ProjectEntity, project_code: str) -> ProjectData:
    return ProjectData(
        project=project_code,
        status=ProgramStatus[entity.status.name.upper()],
        eligible_budget=entity.eligible_budget,
        funding=entity.funding,
        subsidy=entity.subsidy,
        loan=entity.loan,
        funding_percentage=entity.funding_percentage,
        technology=entity.technology,
        deadline=entity.deadline
    )