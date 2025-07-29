from enum import StrEnum, auto
from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional

class AreaType(StrEnum):
    TOWN = auto()
    AREA = auto()

@dataclass
class AreaProperties:
    program_name: str
    autonomous_community: str
    province: str
    municipality: str
    project: str
    grantee: str

    @property
    @abstractmethod
    def type(self) -> AreaType:
        pass


@dataclass
class AreaPropertiesArea(AreaProperties):
    area_code: str
    building_count: int
    house_count: int
    town: Optional[str]

    @property
    def type(self) -> AreaType:
        return AreaType.AREA

@dataclass
class AreaPropertiesTown(AreaProperties):
    town: str
    exception_zone_code: Optional[str] = None
    exception_zone_name: Optional[str] = None

    @property
    def type(self) -> AreaType:
        return AreaType.TOWN