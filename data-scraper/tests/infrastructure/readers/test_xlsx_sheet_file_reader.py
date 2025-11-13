from infrastructure.readers.xlsx_sheet_file_reader import XlsxSheetFileReader
import importlib.resources

async def test_read_xlsx_bytes(test_resource):
    excel_bytes = test_resource("test_excel_file.xlsx").read_bytes()

    reader = XlsxSheetFileReader()

    result = reader.read(excel_bytes)

    assert result == [
        ["First", "Second", "Third"],
        ["One", "Two", "Three"],
        ["Four", "Five", "Six"],
        [None, "Seven", "Eight"],
        ["Nine", None, "Ten"],
        [None, None, "Eleven"]
    ]

async def test_read_xlsx_merged_cells(test_resource):
    excel_bytes = test_resource("test_excel_merged_cells_file.xlsx").read_bytes()

    reader = XlsxSheetFileReader()

    result = reader.read(excel_bytes)

    assert result == [
        ['First', 'Second', 'Third'],
        ['First', 'Two', 'Three'],
        ['Four', 'Five', 'Six'],
        [None, 'Five', 'Eight'],
        ['Nine', None, 'Eight']
    ]
