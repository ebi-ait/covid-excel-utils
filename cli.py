import argparse
import json
import os
from excel.load import get_dict_from_excel
from excel.validate import validate_dict_from_excel


def write_dict(file_path, data_dict):
    file_path = os.path.abspath(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "w") as open_file:
        json.dump(data_dict, open_file, indent=2)
        open_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('file_path', type=str, help='path of excel file to load')
    args = vars(parser.parse_args())
    excel_file_path = args['file_path']

    data = get_dict_from_excel(excel_file_path)
    issues = validate_dict_from_excel(excel_file_path, data)

    if data:
        json_file_path = os.path.splitext(excel_file_path)[0] + '.json'
        write_dict(json_file_path, data)

    if issues:
        issues_file_path = os.path.splitext(excel_file_path)[0] + '_issues.json'
        write_dict(issues_file_path, issues)