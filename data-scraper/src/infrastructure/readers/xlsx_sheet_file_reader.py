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

            # Parse merged cells information FIRST
            merged_ranges = []
            merge_cells_elem = root.find('.//ns:mergeCells', ns)
            if merge_cells_elem is not None:
                for merge_cell in merge_cells_elem.findall('ns:mergeCell', ns):
                    ref = merge_cell.get('ref', '')
                    if ref:
                        parsed_range = self._parse_merge_range(ref)
                        if parsed_range:
                            merged_ranges.append(parsed_range)

            # Third pass: build the data structure
            row_data_dict = {}  # Store all rows by row number
            
            for row in root.findall('.//ns:row', ns):
                row_num = int(row.get('r', 0)) - 1  # Convert to 0-based
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
                
                row_data_dict[row_num] = row_cells
            
            # Apply merged cell values - propagate from top-left to all cells in range
            for merge_range in merged_ranges:
                start_row, start_col, end_row, end_col = merge_range
                
                # Get the value from the top-left cell of the merged range
                merge_value = None
                if start_row in row_data_dict and start_col in row_data_dict[start_row]:
                    merge_value = row_data_dict[start_row][start_col]
                
                # Propagate the value to all cells in the merged range
                for row_idx in range(start_row, end_row + 1):
                    if row_idx not in row_data_dict:
                        row_data_dict[row_idx] = {}
                    for col_idx in range(start_col, end_col + 1):
                        # Only set if not already set or if it's None
                        if col_idx not in row_data_dict[row_idx] or row_data_dict[row_idx][col_idx] is None:
                            row_data_dict[row_idx][col_idx] = merge_value
            
            # Convert dict structure to list structure
            data = []
            if row_data_dict:
                min_row = min(row_data_dict.keys())
                max_row = max(row_data_dict.keys())
                
                # Calculate max column across all rows
                max_col = 0
                for row in row_data_dict.values():
                    if row:
                        max_col = max(max_col, max(row.keys()) if row else 0)
                
                for row_idx in range(min_row, max_row + 1):
                    if row_idx in row_data_dict:
                        row_data = [row_data_dict[row_idx].get(i, None) for i in range(max_col + 1)]
                        data.append(row_data)
                    else:
                        # Empty row
                        data.append([None] * (max_col + 1))
            
            return data

    @staticmethod
    def _parse_merge_range(ref):
        """Parse a merge range like 'A1:D4' into (start_row, start_col, end_row, end_col)."""
        try:
            parts = ref.split(':')
            if len(parts) != 2:
                return None
            
            start_cell = parts[0]
            end_cell = parts[1]
            
            # Parse start cell
            start_col_letter = ''.join(c for c in start_cell if c.isalpha())
            start_row_str = ''.join(c for c in start_cell if c.isdigit())
            if not start_row_str:
                return None
            start_row = int(start_row_str) - 1  # 0-based
            start_col = XlsxSheetFileReader._column_letter_to_index(start_col_letter)
            
            # Parse end cell
            end_col_letter = ''.join(c for c in end_cell if c.isalpha())
            end_row_str = ''.join(c for c in end_cell if c.isdigit())
            if not end_row_str:
                return None
            end_row = int(end_row_str) - 1  # 0-based
            end_col = XlsxSheetFileReader._column_letter_to_index(end_col_letter)
            
            return (start_row, start_col, end_row, end_col)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _column_letter_to_index(column_letter):
        """Convert Excel column letter to 0-based index. A=0, B=1, Z=25, AA=26, etc."""
        index = 0
        for char in column_letter:
            index = index * 26 + (ord(char.upper()) - ord('A') + 1)
        return index - 1