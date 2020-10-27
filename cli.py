import argparse
import json
import os
import sys

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
    parser = argparse.ArgumentParser(description='Parse, Validate and Submit excel files to EBI Resources')
    parser.add_argument('file_path', type=str, help='path of excel file to load')
    parser.add_argument('--biosamples', action='store_true', help='Submit to BioSamples, requires environment variables AAP_USERNAME and AAP_PASSWORD')

    parser.add_argument('--biosamples_url', type=str, default='https://www.ebi.ac.uk/biosamples', help='Override the default URL for BioSamples API.')
    parser.add_argument('--aap_url', type=str, default='https://api.aai.ebi.ac.uk', help='Override the default URL for AAP API.')

    args = vars(parser.parse_args())
    excel_file_path = args['file_path']
    file_name = os.path.splitext(excel_file_path)[0]

    data = get_dict_from_excel(excel_file_path)
    if data:
        json_file_path = file_name + '.json'
        write_dict(json_file_path, data)
        print(f'Data from {len(data)} rows written to: {json_file_path}')

    issues = validate_dict_from_excel(excel_file_path, data)
    if issues:
        issues_file_path = file_name + '_issues.json'
        write_dict(issues_file_path, issues)
        print(f'Issues from {len(issues)} rows written to: {issues_file_path}')

    if args['biosamples']:
        if not data:
            print('No Data to Submit to BioSamples')
            sys.exit(2)

        # ToDo: if issues: Ask user if they want to proceed with detected issues.
        # This may have to wait until we can classify issues into Errors (that will block submission), Warnings and Info

        biosamples_url = args['biosamples_url']
        aap_url = args['aap_url']

        if 'AAP_USERNAME' in os.environ:
            aap_username = os.environ['AAP_USERNAME']
        else:
            print('No AAP_USERNAME detected in os environment variables.')
            sys.exit(2)

        if 'AAP_PASSWORD' in os.environ:
            aap_password = os.environ['AAP_PASSWORD']
        else:
            print('No AAP_PASSWORD detected in os environment variables.')
            sys.exit(2)

        print(f'Attempting to Submit to BioSamples: {biosamples_url}, AAP: {aap_url}')

    sys.exit(0)
