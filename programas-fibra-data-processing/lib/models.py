from enum import StrEnum, auto
from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional

class ProgramType(StrEnum):
    UNICO = auto()
    PEBA = auto()

@dataclass
class AreaProperties:
    autonomous_community: str
    province: str
    municipality: str
    project: str
    grantee: str

    @property
    @abstractmethod
    def program_type(self) -> ProgramType:
        pass


@dataclass
class AreaPropertiesUNICO(AreaProperties):
    area_code: str
    building_count: int
    house_count: int

    @property
    def program_type(self) -> ProgramType:
        return ProgramType.UNICO

@dataclass
class AreaPropertiesPEBA(AreaProperties):
    town: str
    exception_zone_code: Optional[str] = None
    exception_zone_name: Optional[str] = None

    @property
    def program_type(self) -> ProgramType:
        return ProgramType.PEBA