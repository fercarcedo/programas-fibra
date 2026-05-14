from dataclasses import dataclass

@dataclass
class ProgramUpdateResult:
    file_url: str
    program_name: str
    last_updated: int
    page_url: str = ""