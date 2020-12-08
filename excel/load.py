from contextlib import closing

from openpyxl import load_workbook
from .clean import clean_entity_name, clean_name, value_populated


class ExcelLoader:
    def __init__(self, excel_path: str, sheet_index=0):
        # ToDo: Accept param for number of header rows, columns
        self.__path = excel_path
        self.__sheet_index = sheet_index
        with closing(load_workbook(filename=self.__path, read_only=True, keep_links=False)) as workbook:
            worksheet = workbook.worksheets[self.__sheet_index]
            self.column_map = self.get_column_map(worksheet)
            self.data = self.get_data(worksheet, self.column_map)

    @staticmethod
    def get_column_map(worksheet) -> dict:
        # Uses iter_rows for faster reads, requires workbook read_only=True
        column_map = {}
        header_rows = []
        object_name = False
        for row in worksheet.iter_rows(min_col=2, max_row=5):
            header_rows.append(row)
        for column_index in range(0, len(header_rows[0])):
            object_cell = header_rows[0][column_index]
            attribute_cell = header_rows[1][column_index]
            column_info = {}

            # Update Object Name otherwise use most recent Object found
            if object_cell.value is not None:
                object_name = clean_entity_name(object_cell.value)
            if object_name:
                column_info['object'] = object_name
            if attribute_cell.value is not None:
                column_info['attribute'] = clean_name(attribute_cell.value)
                column_map[attribute_cell.column_letter] = column_info
        return column_map

    @staticmethod
    def get_data(worksheet, column_map: dict):
        data = {}
        # Import cell values into data object
        # Uses .iter_rows for faster reads, requires workbook read_only=True
        row_index = 6
        for row in worksheet.iter_rows(min_row=row_index, min_col=2):
            row_data = {}
            for cell in row:
                if cell.value is not None and value_populated(cell.value):
                    if cell.is_date:
                        value = cell.value.date().isoformat()
                    else:
                        value = str(cell.value).strip()
                    object_name = column_map[cell.column_letter]['object']
                    attribute_name = column_map[cell.column_letter]['attribute']
                    row_data.setdefault(object_name, {})[attribute_name] = value
            if len(row_data) > 0:
                data[row_index] = row_data
            row_index = row_index + 1
        return data
