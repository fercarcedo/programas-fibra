from domain.program_update_result import ProgramUpdateResult
from domain.readers.sheet_file_reader import SheetFileReader
from workers import fetch
import json

class ProcessProgramsUseCase:
    def __init__(self, sheet_reader: SheetFileReader):
        self.sheet_reader = sheet_reader

    async def execute(self, program: ProgramUpdateResult):
        response = await fetch(program.file_url)

        if response is None or not response.ok:
            return None

        response_bytes = await response.bytes()
        sheet_data = self.sheet_reader.read(response_bytes)
        print(sheet_data)

        return "END"
        