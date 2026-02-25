from domain.projects_status import ProjectsStatus
from infrastructure.entity.projects_status_entity import ProgramStatusEntity, ProjectStatusInfoEntity, ProjectsStatusEntity

def to_entity(projects_status: ProjectsStatus) -> ProjectsStatusEntity:
    entity_map: ProjectsStatusEntity = {}

    for project_id, data in projects_status.items():
        entity_map[project_id] = ProjectStatusInfoEntity(
            status=ProgramStatusEntity[data.status.name],
            deadline=data.deadline
        )

    return entity_map