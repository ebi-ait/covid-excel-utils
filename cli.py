import argparse
import json
import os
import sys

from services.biosamples import AapClient, BioSamples
from excel.load import get_dict_from_excel
from excel.validate import validate_dict_from_excel
from validation.schema import SchemaValidation


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
    issues_file_path = file_name + '_issues.json'

    data = get_dict_from_excel(excel_file_path)
    if not data:
        print(f'No Data imported from: {excel_file_path}')
        sys.exit(0)

    write_dict(json_file_path, data)
    print(f'Data from {len(data)} rows written to: {json_file_path}')

    try:
        schema_validation = SchemaValidation("http://localhost:3020/validate")
        issues = schema_validation.validate_data(data)
    except Exception as error:
        print('Error validating schema, using best guess validation.')
        issues = validate_dict_from_excel(excel_file_path, data)
    
    if issues:
        write_dict(json_file_path, data)
        write_dict(issues_file_path, issues)
        print(f'Issues from {len(issues)} rows written to: {issues_file_path} and into: {json_file_path}')

    if args['biosamples']:
        if issues:
            user_text = input(f'Issues from {len(issues)} rows detected. Continue with BioSamples Submission? (y/N)?:')
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
                    row['sample']['request'] = biosamples.encode_sample(row['sample'])
                    sample_count = sample_count + 1
                except Exception as error:
                    error_msg = f'Encoding Error: {error}'
                    issues.setdefault(str(row['row']), []).append(error_msg)
                    row['sample'].setdefault('errors', []).append(error_msg)
                    error_count = error_count + 1
        if error_count:
            write_dict(issues_file_path, issues)
            print(f'Data from {error_count} errors written to: {issues_file_path}')
        write_dict(json_file_path, data)
        print(f'Data from {sample_count} BioSamples conversions written to: {json_file_path}')

        biosample_count = 0
        error_count = 0
        for row in data:
            if 'sample' in row and 'request' in row['sample']:
                try:
                    row['sample']['biosample'] = biosamples.send_sample(row['sample']['request'])
                    row['sample'].pop('request')
                    biosample_count = biosample_count + 1
                except Exception as error:
                    error_msg = f'BioSamples Error: {error}'
                    issues.setdefault(str(row['row']), []).append(error_msg)
                    row['sample'].setdefault('errors', []).append(error_msg)
                    error_count = error_count + 1
        if error_count:
            write_dict(issues_file_path, issues)
            print(f'Data from {error_count} errors written to: {issues_file_path}')
        write_dict(json_file_path, data)
        print(f'Data from {biosample_count} BioSamples responses written to: {json_file_path}')

    sys.exit(0)
