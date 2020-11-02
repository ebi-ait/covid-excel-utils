import argparse
import json
import os
import sys

from excel.load import get_dict_from_excel
from excel.validate import validate_dict_from_excel
from services.biosamples import AapClient, BioSamples


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
    
    parser.add_argument('--biosamples_domain', type=str, help='Override the BioSamples domain rather than detect the domain from the excel file.')
    parser.add_argument('--biosamples_url', type=str, default='https://www.ebi.ac.uk/biosamples', help='Override the default URL for BioSamples API.')
    parser.add_argument('--aap_url', type=str, default='https://api.aai.ebi.ac.uk', help='Override the default URL for AAP API.')

    args = vars(parser.parse_args())
    excel_file_path = args['file_path']
    file_name = os.path.splitext(excel_file_path)[0]
    json_file_path = file_name + '.json'
        
    data = get_dict_from_excel(excel_file_path)
    if data:
        write_dict(json_file_path, data)
        print(f'Data from {len(data)} rows written to: {json_file_path}')

    issues = validate_dict_from_excel(excel_file_path, data)
    # Return issues as a dictionary of row_index: List[row_errors]
    # This will allow issues object to be appended by row_index in following validation and submission code
    if issues:
        issues_file_path = file_name + '_issues.json'
        write_dict(issues_file_path, issues)
        print(f'Issues from {len(issues)} rows written to: {issues_file_path}')
    
    if args['biosamples']:
        if not data:
            print('No Data to Submit to BioSamples')
            sys.exit(2)

        if issues:
            user_text = input(f'{len(issues)} issues detected. Continue with BioSamples Submission? (y/N)?:')
            if not user_text.lower().startswith('y'):
                print('Exiting')
                sys.exit(0)

        aap_url = args['aap_url']
        url = args['biosamples_url']
        domain = args['biosamples_domain']

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

        print(f'Attempting to Submit to BioSamples: {url}, AAP: {aap_url}')
        aap_client = AapClient(url=aap_url, username=aap_username, password=aap_password)
        biosamples = BioSamples(aap_client, url, domain)
        sample_count = 0
        error_count = 0
        for row in data:
            if 'sample' in row:
                try:
                    # ToDo: Maybe store this in row['sample']['request']
                    row['sample_request'] = biosamples.encode_sample(row['sample'])
                    sample_count = sample_count + 1
                except Exception as error:
                    # ToDo: Also write to issues
                    # ToDo: Maybe append this to row['sample']['errors']
                    # row['sample'].setdefault('errors', []).append()
                    row.setdefault('sample_request', {})['error'] = f'Encoding Error: {error}'
                    error_count = error_count + 1
        write_dict(json_file_path, data)
        print(f'Data from {sample_count} BioSamples conversions and {error_count} errors written to: {json_file_path}')

        biosample_count = 0
        error_count = 0
        for row in data:
            if 'sample_request' in row and 'error' not in row['sample_request']:
                try:
                    # ToDo: Maybe store this in row['sample']['response']
                    row['sample_response'] = biosamples.send_sample(row['sample_request'])
                    biosample_count = biosample_count + 1
                except Exception as error:
                    # ToDo: Also write to issues
                    # ToDo: Maybe append this to row['sample']['errors']
                    # row['sample'].setdefault('errors', []).append()
                    row.setdefault('sample_response', {})['error'] = f'BioSamples Error: {error}'
                    error_count = error_count + 1
        write_dict(json_file_path, data)
        print(f'Data from {biosample_count} BioSamples responses and {error_count} errors written to: {json_file_path}')


    sys.exit(0)
