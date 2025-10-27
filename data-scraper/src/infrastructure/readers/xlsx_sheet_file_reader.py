from domain.readers.sheet_file_reader import SheetFileReader
from io import BytesIO
import xml.etree.ElementTree as ET
from zipfile import ZipFile

class XlsxSheetFileReader(SheetFileReader):
    def read(self, bytes, sheet_number=1):
        with ZipFile(BytesIO(bytes), 'r') as zip_ref:
            # First pass: read the sheet and collect used shared string indices
            sheet_path = f'xl/worksheets/sheet{sheet_number}.xml'

            try:
                sheet_xml = zip_ref.read(sheet_path)
            except KeyError:
                raise ValueError(f"Sheet {sheet_number} not found in workbook")

            # Parse sheet to find which shared strings are referenced
            used_indices = set()
            root = ET.fromstring(sheet_xml)

            # Find all cells with type 's' (shared string)
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for cell in root.findall('.//ns:c[@t="s"]', ns):
                v = cell.find('ns:v', ns)
                if v is not None and v.text:
                    used_indices.add(int(v.text))

            # Second pass: stream parse shared strings, only loading what we need
            shared_strings = {}
            if used_indices:
                try:
                    with zip_ref.open('xl/sharedStrings.xml') as ss_file:
                        # Use iterparse for streaming XML parsing
                        context = ET.iterparse(ss_file, events=('end',))
                        current_idx = 0

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

                except KeyError:
                    pass  # No shared strings file

            # Third pass: build the data structure
            data = []
            for row in root.findall('.//ns:row', ns):
                row_cells = {}  # Use dict to track by column
                
                for cell in row.findall('ns:c', ns):
                    # Get cell reference like "A1", "B5", etc.
                    cell_ref = cell.get('r', '')
                    
                    # Extract column letter(s) from reference
                    col_letter = ''.join(c for c in cell_ref if c.isalpha())
                    col_idx = self._column_letter_to_index(col_letter)
                    
                    cell_type = cell.get('t', '')
                    v = cell.find('ns:v', ns)
                    
                    if v is not None and v.text:
                        if cell_type == 's':  # Shared string
                            idx = int(v.text)
                            row_cells[col_idx] = shared_strings.get(idx, '')
                        elif cell_type == 'b':  # Boolean
                            row_cells[col_idx] = v.text == '1'
                        elif cell_type == 'str':  # Inline string
                            row_cells[col_idx] = v.text
                        else:  # Number
                            try:
                                if '.' not in v.text:
                                    row_cells[col_idx] = int(v.text)
                                else:
                                    row_cells[col_idx] = float(v.text)
                            except ValueError:
                                row_cells[col_idx] = v.text
                    else:
                        row_cells[col_idx] = None
                
                # Convert dict to list, filling gaps with None
                if row_cells:
                    max_col = max(row_cells.keys())
                    row_data = [row_cells.get(i, None) for i in range(max_col + 1)]
                    data.append(row_data)
            
            return data

    @staticmethod
    def _column_letter_to_index(column_letter):
        """Convert Excel column letter to 0-based index. A=0, B=1, Z=25, AA=26, etc."""
        index = 0
        for char in column_letter:
            index = index * 26 + (ord(char.upper()) - ord('A') + 1)
        return index - 1