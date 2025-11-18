from domain.program_data import ProjectData
from infrastructure.entity.project_entity import ProjectEntity, ProgramStatus

def to_entity(project: ProjectData) -> ProjectEntity:
    return ProjectEntity(
        status=ProgramStatus[project.status.name],
        eligible_budget=project.eligible_budget,
        funding=project.funding,
        subsidy=project.subsidy,
        loan=project.loan,
        funding_percentage=project.funding_percentage,
        technology=project.technology,
        deadline=project.deadline
    )