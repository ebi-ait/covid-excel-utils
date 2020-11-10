from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
from validation.schema import translate_to_human
from .load import ExcelLoader

class ExcelMarkup(ExcelLoader):
    def __init__(self, excel_path: str, sheet_index=0):
        super().__init__(excel_path, sheet_index)
        self.__path = excel_path
        self.__sheet_index = sheet_index
        self.book = load_workbook(filename=excel_path, keep_links=False)
        self.sheet = self.book.worksheets[self.__sheet_index]
        self.attribute_map = self.reverse_column_map(self.column_map)
    
    def save(self):
        self.book.save(self.__path)

    def clear_style(self):
        self.sheet.delete_cols(1)
        self.sheet.insert_cols(1)
        self.sheet['A1'] = 'errors'
        self.sheet['A2'] = 'summary'
        for row in self.sheet.iter_rows(min_row=6):
            for cell in row:
                cell.fill = PatternFill()
                cell.comment = None
        self.save()
        
    def style_errors(self, errors):
        error_fill = PatternFill(fill_type='solid', start_color='FF0000')
        
        for row_index, entities in errors.items():
            error_count = 0
            for entity_type, entity_errors in entities.items():
                for attribute_error in entity_errors:
                    attribute_name = attribute_error['dataPath'].strip('.')
                    human_errors = translate_to_human(
                        entity_type,
                        attribute_name,
                        attribute_error['errors']
                    )
                    human_error = '\r\n'.join(human_errors)
                    error_count = error_count + len(human_errors)
                    cell_index = self.lookup_cell_index(entity_type, attribute_name, row_index)
                    comment = Comment(human_error, f'{entity_type} Validaion')
                    comment.width = 500
                    comment.height = 100
                    self.sheet[cell_index].comment = comment
                    self.sheet[cell_index].fill = error_fill
            if error_count:
                self.sheet[f'A{row_index}'] = f'{error_count} Errors'
                self.sheet[f'A{row_index}'].fill = error_fill
        self.save()

    def set_filter(self):
        pass

    def lookup_cell_index(self, entity_type, attribute, row):
        attribute_key = f'{entity_type}.{attribute}'
        column_letter =  self.attribute_map[attribute_key]
        return f'{column_letter}{row}'

    @staticmethod
    def reverse_column_map(column_map: dict) -> dict:
        attribute_map = {}
        for letter, info in column_map.items():
            attribute_key = f"{info['object']}.{info['attribute']}"
            attribute_map[attribute_key] = letter
        return attribute_map
