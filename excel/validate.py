from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.datavalidation import DataValidationList
from datetime import date
from excel.clean import clean_object, clean_name


def valid_date(value: str) -> bool:
    try:
        fromiso = date.fromisoformat(value)
        return True
    except Exception:
        return False


def object_has_attribute(object_data: dict, attribute: str) -> bool:
    return attribute in object_data and object_data[attribute].strip() not in ['NP', 'NA', 'NC']


def object_has_accession(object_data: dict):
    return object_has_attribute(object_data, 'study_accession') or object_has_attribute(object_data, 'sample_accession')


def validate_object(object_validation: dict, object_data: dict):
    errors = []
    for attribute_name in object_validation.keys():
        attribute_info = object_validation[attribute_name]
        if not object_has_attribute(object_data, attribute_name):
            if 'mandatory' in attribute_info and not object_has_accession(object_data):
                mandatory = attribute_info['mandatory'].strip()
                if mandatory == 'M':
                    errors.append('Error: Mandatory Atrribute {} is missing.'.format(attribute_name))
                elif mandatory == 'R':
                    errors.append('Warning: Reccomended Atrribute {} is missing.'.format(attribute_name))
                elif mandatory != 'O':
                    errors.append('Info: Atrribute {} may be required. {}'.format(attribute_name, mandatory))
        else:
            value = object_data[attribute_name]
            if 'format' in attribute_info and attribute_info['format'] == 'YYYY-MM-DD' and not valid_date(value):
                errors.append('Error: {} has value {}, which is not in date format YYYY-MM-DD.'.format(attribute_name, value))
            if 'accepted_values' in attribute_info and value.lower() not in attribute_info['accepted_values']:
                errors.append('Error: {} has value {} which is not in list of accepted values. {}'.format(attribute_name, value, attribute_info['accepted_values']))
    if errors:
        object_data['errors'] = errors
    return errors


def validate_data_row(validation_map: dict, data_row):
    object_errors = []
    other_errors = []
    all_errors = []
    for object_name in validation_map.keys():
        if object_name not in data_row:
            object_errors.append('Error: Object {} is missing.'.format(object_name))
        else:
            other_errors.extend(validate_object(validation_map[object_name], data_row[object_name]))
    if object_errors:
        data_row['errors'] = object_errors
    all_errors.extend(object_errors)
    all_errors.extend(other_errors)
    return all_errors

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
                    # Accepted values encoded directly into validation formula
                    validation_list[cell_range.coord] = validation.formula1.replace('"', '').lower().split(',')
                    # ToDo: Support validation that refereces a table of values on sheet "Accepted_Values"
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
                    column_object['accepted_values'] = excel_validations[format_cell.coordinate]
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