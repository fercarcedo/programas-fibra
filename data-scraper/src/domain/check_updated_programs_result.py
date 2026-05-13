from dataclasses import dataclass
from domain.program_update_result import ProgramUpdateResult

@dataclass
class SkippedProgram:
    program_name: str
    url: str
    reason: str

@dataclass
class CheckUpdatedProgramsResult:
    updated: list[ProgramUpdateResult]
    skipped: list[SkippedProgram]
