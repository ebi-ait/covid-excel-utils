from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.datavalidation import DataValidationList
from excel.clean import clean_object, clean_name


def validate_object(object_validation: dict, object_data: dict):
    errors = []
    # ToDo: Validate object
    return errors


def validate_data_row(validation_map: dict, data_row):
    object_errors = []
    other_errors = []
    for object_name in validation_map.keys():
        if object_name not in data_row:
            object_errors.append('Error: Object "{}" is missing.'.format(object_name))
        else:
            other_errors.extend(validate_object(validation_map[object_name], data_row[object_name]))
    if object_errors:
        data_row['errors'] = object_errors
    object_errors.extend(other_errors)
    return object_errors

def validate_data_list(validation_map: dict, data):
    validation_report = []
    for item in data:
        row_errors = validate_data_row(validation_map, item)
        if row_errors:
            validation_report.append({ item['row']: row_errors })
    return validation_report


def get_excel_validations(validations: DataValidationList):
    validation_list = {}
    # If Excel's data vaidation is used for displaying accepted values on header row,
    # Replace single selected value with all accepted values
    for validation in validations:
        if validation.validation_type == 'list':
            for cell_range in validation.ranges:
                if cell_range.min_col == cell_range.max_col and cell_range.min_row == 4 and cell_range.max_row == 4:
                    validation_list[cell_range.coord] = validation.formula1.replace('"', '').split(',')
    return validation_list


def get_validation_map(worksheet: Worksheet, excel_validations: dict = None) -> dict:
    validation = {}
    name = False
    for column in worksheet.iter_cols(min_col=2, max_row=5):
        cells = []
        for cell in column:
            cells.append(cell)

        object_cell = cells[0]
        attribute_cell = cells[1]
        mandatory_cell = cells[2]
        format_cell = cells[3]
        units_cell = cells[4]

        # Update Object Name otherwise use most recent Object found
        if object_cell.value is not None:
            name = clean_object(object_cell.value)
        if name:
            if attribute_cell.value is not None:
                attribute = clean_name(attribute_cell.value)
                column_object = {}

                if mandatory_cell.value is not None:
                    column_object['mandatory'] = mandatory_cell.value   

                if validation and format_cell.coordinate in excel_validations:
                    column_object['format'] = excel_validations[format_cell.coordinate]
                elif format_cell.value is not None:
                    column_object['format'] = format_cell.value
        
                if units_cell.value is not None:
                    column_object['units'] = units_cell.value

                if name not in validation:
                    validation[name] = {}
                validation[name][attribute] = column_object
    return validation


def get_validation_dict_from_excel(file_path, sheet_index=0):
    workbook = load_workbook(filename=file_path, read_only=False, keep_links=False)
    worksheet = workbook.worksheets[sheet_index]
    try:
        validations = get_excel_validations(worksheet.data_validations.dataValidation)
        return get_validation_map(worksheet, validations)
    finally:
        workbook.close()


def validate_dict_from_excel(file_path, data, sheet_index=0):
    validation_map = get_validation_dict_from_excel(file_path, sheet_index)
    return validate_data_list(validation_map, data)