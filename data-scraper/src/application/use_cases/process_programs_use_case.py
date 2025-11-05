from domain.program_update_result import ProgramUpdateResult
from domain.readers.sheet_file_reader import SheetFileReader
from workers import fetch
import json
from domain.program_data import ProgramData, ProgramStatus, ProjectData
from datetime import datetime, timedelta, date

class ProcessProgramsUseCase:
    def __init__(self, sheet_reader: SheetFileReader):
        self.sheet_reader = sheet_reader

    async def execute(self, program: ProgramUpdateResult) -> ProgramData:
        response = await fetch(program.file_url)

        if response is None or not response.ok:
            return None

        response_bytes = await response.bytes()
        sheet_data = self.sheet_reader.read(response_bytes)
        header_index, header = self._get_header_row(sheet_data)

        projects = self._process_sheet_data(sheet_data, header_index, header)
        return ProgramData(projects=projects)

    def _not_none_cells(self, row: list[str]) -> list[str]:
        return [cell for cell in row if cell is not None]

    def _process_sheet_data(self, sheet_data: list[list[str]], header_index: int, header: list[str]) -> list[ProjectData]:
        result = []
        for index in range(header_index + 1, len(sheet_data)):
            if len(self._not_none_cells(header)) - len(self._not_none_cells(sheet_data[index])) <= 1:
                row = dict(zip(header, sheet_data[index]))
                deadline = self._get_deadline_from_row(row['FECHA FINALIZACIÓN'] if 'FECHA FINALIZACIÓN' in row else None)
                subsidy_value = self._get_subsidy_from_row(row)
                subsidy = round(subsidy_value, 2) if subsidy_value is not None else None
                erdf_advance_payment = round(row['ANTICIPO FEDER (€)'], 2) if 'ANTICIPO FEDER (€)' in row else None
                eligible_budget_value = row['PRESUPUESTO  FINANCIABLE (€)'] if 'PRESUPUESTO  FINANCIABLE (€)' in row else row['INVERSIÓN PREVISTA (€)']
                funding_value = row['AYUDA  (€)'] if 'AYUDA  (€)' in row else row['PRÉSTAMO CONCEDIDO (€)']
                funding_percentage_value = row['% AYUDA'] if '% AYUDA' in row else row['INTENSIDAD DE LA AYUDA']
                project_data = ProjectData(
                    project=row['EXPEDIENTE'] if 'EXPEDIENTE' in row else row['PROYECTO'],
                    status=self._get_status_from_Row(row['SITUACIÓN']),
                    eligible_budget=round(eligible_budget_value, 2),
                    funding=round(funding_value, 2),
                    subsidy=subsidy,
                    erdf_advance_payment=erdf_advance_payment,
                    funding_percentage=round(funding_percentage_value),
                    technology=row['TECNOLOGÍA'],
                    deadline=deadline,
                    last_updated=0
                )
                result.append(project_data)
        return result

    def _get_subsidy_from_row(self, row: dict[str, str]) -> str:
        if 'SUBVENCION (€)' in row:
            return row['SUBVENCION (€)']
        
        if 'SUBVENCIÓN CONCEDIDA (€)' in row:
            return row['SUBVENCIÓN CONCEDIDA (€)']
        
        return None
  
    def _get_deadline_from_row(self, deadline_value: str) -> date:
        if deadline_value is None:
            return None
        
        return (datetime(1899, 12, 30) + timedelta(days=int(deadline_value))).date()

    def _get_status_from_Row(self, status_value: str) -> ProgramStatus:
        status_value_upper = status_value.upper()
        if status_value_upper == 'EN EJECUCIÓN':
            return ProgramStatus.IN_PROGRESS
        if status_value_upper == 'CANCELADO':
            return ProgramStatus.CANCELLED
        return ProgramStatus.FINISHED

    def _get_header_row(self, sheet_data: dict[str, str]) -> tuple[int, list[str]]:
        for index, row in enumerate(sheet_data):
            if all(v is None for v in row) or all(v is None for v in row[1:]):
                continue
            upper_row = [v.upper() if v is not None else v for v in row]
            if not "EXPEDIENTE" in upper_row and not "PROYECTO" in upper_row:
                continue
            return index, upper_row