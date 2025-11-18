from domain.program_update_result import ProgramUpdateResult
from domain.readers.sheet_file_reader import SheetFileReader
from workers import fetch
import json
from domain.program_data import ProgramData, ProgramStatus, ProjectData
from datetime import datetime, timedelta, date
from domain.repositories.program_repository import ProgramRepository
import time

class ProcessProgramsUseCase:
    def __init__(self, sheet_reader: SheetFileReader, program_repository: ProgramRepository):
        self.sheet_reader = sheet_reader
        self.program_repository = program_repository

    async def execute(self, program: ProgramUpdateResult) -> ProgramData:
        response = await fetch(program.file_url)

        if response is None or not response.ok:
            return None

        response_bytes = await response.bytes()
        sheet_data = self.sheet_reader.read(response_bytes)
        header_index, header = self._get_header_row(sheet_data)

        projects = self._process_sheet_data(sheet_data, header_index, header)
        for project in projects:
            await self.program_repository.put_project(project)
        await self.program_repository.put_last_update(program.program_name, int(time.time()))
        return ProgramData(projects=projects)

    def _not_none_cells(self, row: list[str]) -> list[str]:
        return [cell for cell in row if cell is not None]

    def _process_sheet_data(self, sheet_data: list[list[str]], header_index: int, header: list[str]) -> list[ProjectData]:
        result = []
        for index in range(header_index + 1, len(sheet_data)):
            if len(self._not_none_cells(header)) - len(self._not_none_cells(sheet_data[index])) <= 1:
                row = dict(zip(header, sheet_data[index]))
                project=row['EXPEDIENTE'] if 'EXPEDIENTE' in row else row['PROYECTO']
                if project and project.startswith('TSI-'):
                    deadline = self._get_deadline_from_row(row['FECHA FINALIZACIÓN'] if 'FECHA FINALIZACIÓN' in row else None)
                    subsidy_value = self._get_subsidy_from_row(row)
                    subsidy = round(subsidy_value, 2) if subsidy_value is not None else None
                    loan_value = self._get_loan_from_row(row)
                    loan = round(loan_value, 2) if loan_value is not None else None
                    eligible_budget_value = self._get_eligible_budget_from_row(row)
                    funding_value = self._get_funding_value_from_row(row, subsidy, loan)
                    funding_percentage = self._get_funding_percentage_from_row(row, funding_value, eligible_budget_value)
                    project_data = ProjectData(
                        project=project,
                        status=self._get_status_from_Row(row['SITUACIÓN']),
                        eligible_budget=round(eligible_budget_value, 2),
                        funding=round(funding_value, 2),
                        subsidy=subsidy,
                        loan=loan,
                        funding_percentage=funding_percentage,
                        technology=row['TECNOLOGÍA'],
                        deadline=deadline,
                    )
                    result.append(project_data)
        return result

    def _get_funding_value_from_row(self, row: dict[str, str], subsidy: float, loan: float) -> float:
        if 'AYUDA  (€)' in row:
            return float(row['AYUDA  (€)'])

        return subsidy + loan

    def _get_funding_percentage_from_row(self, row: dict[str, str], funding: float, eligible_budget: float) -> float:
        if "INTENSIDAD DE LA AYUDA" in row:
            return round(float(row["INTENSIDAD DE LA AYUDA"]))

        return round((funding / eligible_budget) * 100)

    def _get_subsidy_from_row(self, row: dict[str, str]) -> float:
        if 'SUBVENCION (€)' in row:
            return float(row['SUBVENCION (€)'])

        if 'SUBVENCIÓN CONCEDIDA (€)' in row:
            return float(row['SUBVENCIÓN CONCEDIDA (€)'])

        return None

    def _get_eligible_budget_from_row(self, row: dict[str, str]) -> float:
        if 'PRESUPUESTO  FINANCIABLE (€)' in row:
            return float(row['PRESUPUESTO  FINANCIABLE (€)'])

        if 'PRESUPUESTO_FINANCIABLE (€)' in row:
            return float(row['PRESUPUESTO_FINANCIABLE (€)'])

        if 'INVERSIÓN PREVISTA (€)' in row:
            return float(row['INVERSIÓN PREVISTA (€)'])

        return None

    def _get_loan_from_row(self, row: dict[str, str]) -> float:
        if 'ANTICIPO FEDER (€)' in row:
            return float(row['ANTICIPO FEDER (€)'])

        if 'ANTICIPO (€)' in row:
            return float(row['ANTICIPO (€)'])

        if 'PRÉSTAMO CONCEDIDO (€)' in row:
            return float(row['PRÉSTAMO CONCEDIDO (€)'])

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