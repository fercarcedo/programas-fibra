from domain.program_update_result import ProgramUpdateResult
from workers import fetch
from io import BytesIO
import json
import warnings
import zipfile
import io
import xml.etree.ElementTree as ET

class ProcessProgramsStep:
    def __init__(self, env):
        self.env = env

    async def run(self, program: ProgramUpdateResult):
        response = await fetch(program.file_url)

        if response is None or not response.ok:
            return None

        response_bytes = await response.bytes()
        print(self._read_xlsx_bytes(response_bytes))

        return "END"

    def _read_xlsx_bytes(self, excel_bytes, sheet_number=1):
        """
        Read an Excel file by parsing its XML structure without dependencies.
        Only loads shared strings that are actually used in the specified sheet.

        Args:
            excel_bytes: Bytes array of the .xlsx file (e.g., from requests.get().content)
            sheet_number: Sheet number to read (1-indexed, default=1)

        Returns:
            List of lists representing rows and cells
        """
        with zipfile.ZipFile(BytesIO(excel_bytes), 'r') as zip_ref:
            # First pass: read the sheet and collect used shared string indices
            print("Inside zip file")
            sheet_path = f'xl/worksheets/sheet{sheet_number}.xml'

            try:
                print("Reading sheet")
                sheet_xml = zip_ref.read(sheet_path)
            except KeyError:
                raise ValueError(f"Sheet {sheet_number} not found in workbook")

            # Parse sheet to find which shared strings are referenced
            used_indices = set()
            root = ET.fromstring(sheet_xml)

            print("Parsed sheet")

            # Find all cells with type 's' (shared string)
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for cell in root.findall('.//ns:c[@t="s"]', ns):
                v = cell.find('ns:v', ns)
                if v is not None and v.text:
                    used_indices.add(int(v.text))

            print("Finished parsing indices")

            # Second pass: stream parse shared strings, only loading what we need
            shared_strings = {}
            if used_indices:
                try:
                    with zip_ref.open('xl/sharedStrings.xml') as ss_file:
                        print("Opened sharedstrings")
                        # Use iterparse for streaming XML parsing
                        context = ET.iterparse(ss_file, events=('end',))
                        current_idx = 0

                        print("Started iterating context")
                        for event, elem in context:
                            # Only process <si> elements (shared string items)
                            if elem.tag.endswith('si'):
                                if current_idx in used_indices:
                                    # Extract text from <t> tags
                                    text_parts = []
                                    for t in elem.iter():
                                        if t.tag.endswith('t') and t.text:
                                            text_parts.append(t.text)
                                    shared_strings[current_idx] = ''.join(text_parts)

                                current_idx += 1
                                # Clear the element to free memory
                                elem.clear()

                                # Early exit if we've found all needed strings
                                if len(shared_strings) == len(used_indices):
                                    break

                        print("Finished iterating context")

                except KeyError:
                    pass  # No shared strings file

            # Third pass: build the data structure
            data = []
            for row in root.findall('.//ns:row', ns):
                row_data = []

                for cell in row.findall('ns:c', ns):
                    cell_type = cell.get('t', '')
                    v = cell.find('ns:v', ns)

                    if v is not None and v.text:
                        if cell_type == 's':  # Shared string
                            idx = int(v.text)
                            row_data.append(shared_strings.get(idx, ''))
                        elif cell_type == 'b':  # Boolean
                            row_data.append(v.text == '1')
                        elif cell_type == 'str':  # Inline string
                            row_data.append(v.text)
                        else:  # Number
                            try:
                                # Try integer first
                                if '.' not in v.text:
                                    row_data.append(int(v.text))
                                else:
                                    row_data.append(float(v.text))
                            except ValueError:
                                row_data.append(v.text)
                    else:
                        row_data.append(None)

                if row_data:  # Only add non-empty rows
                    data.append(row_data)

            return data
        