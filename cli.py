import argparse
import json
import os
import sys

from services.biosamples import AapClient, BioSamples
from excel.markup import ExcelMarkup
from validation.schema import SchemaValidation


def write_dict(file_path, data_dict):
    file_path = os.path.abspath(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "w") as open_file:
        json.dump(data_dict, open_file, indent=2)
        open_file.close()


def close(message, status=0, xls_file: ExcelMarkup = None, main_args=None):
    if xls_file and main_args['output'] in ['all', 'excel']:
        xls_file.markup_with_errors()
        xls_file.book.close()
        print(f"Excel file updated: {main_args['file_path']}")
    if xls_file and main_args['output'] in ['all', 'json']:
        file_path = main_args['file_path']
        file_name = os.path.splitext(file_path)[0]
        json_file_path = file_name + '.json'
        write_dict(json_file_path, xls_file.rows)
        print(f'JSON output written to: {json_file_path}')

        issues_file_path = file_name + '_issues.json'
        write_dict(issues_file_path, xls_file.errors)
        print(f'JSON issues written to: {issues_file_path}')
    print(message)
    sys.exit(status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, Validate and Submit excel files to EBI Resources'
    )
    parser.add_argument(
        'file_path', type=str,
        help='path of excel file to load'
    )
    parser.add_argument(
        '--output', type=str,
        choices=['all', 'excel', 'json'],
        default='excel',
        help='Where to save the validation and submission output.'
    )
    parser.add_argument(
        '--biosamples', action='store_true',
        help='Submit to BioSamples, requires environment variables AAP_USERNAME and AAP_PASSWORD'
    )
    parser.add_argument(
        '--biosamples_domain', type=str,
        help='Override the BioSamples domain rather than detect the domain from the excel file.'
    )
    parser.add_argument(
        '--biosamples_url', type=str, default='https://www.ebi.ac.uk/biosamples',
        help='Override the default URL for BioSamples API.'
    )
    parser.add_argument(
        '--aap_url', type=str, default='https://api.aai.ebi.ac.uk',
        help='Override the default URL for AAP API.'
    )

    args = vars(parser.parse_args())
    excel_file_path = args['file_path']
    excel_file = ExcelMarkup(excel_file_path)
    if not excel_file.rows:
        close(f'No Data imported from: {excel_file_path}', status=0)

    schema_validation = SchemaValidation("http://localhost:3020/validate")
    try:
        schema_validation.validate_excel(excel_file)
    except Exception as error:
        # ToDo: Refactor Best Guess validation to match output of schema_validation
        close('Error validating schema, Exiting.', status=2)

    if args['biosamples']:
        exit_status = None
        exit_message = ''
        if excel_file.errors:
            user_text = input(
                f'Issues from {len(excel_file.errors)} rows detected. Continue with BioSamples Submission? (y/N)?:')
            if not user_text.lower().startswith('y'):
                exit_status = 0
                exit_message = 'Exiting'

        aap_url = args['aap_url']
        url = args['biosamples_url']
        domain = args['biosamples_domain']

        if 'AAP_USERNAME' in os.environ:
            aap_username = os.environ['AAP_USERNAME']
        else:
            exit_status = 2
            exit_message = 'No AAP_USERNAME detected in os environment variables.'

        if 'AAP_PASSWORD' in os.environ:
            aap_password = os.environ['AAP_PASSWORD']
        else:
            exit_status = 2
            exit_message = 'No AAP_PASSWORD detected in os environment variables.'

        if exit_status or exit_message:
            close(exit_message, exit_status, excel_file, args)

        print(f'Attempting to Submit to BioSamples: {url}, AAP: {aap_url}')
        aap_client = AapClient(url=aap_url, username=aap_username, password=aap_password)
        biosamples = BioSamples(aap_client, url, domain)
        for row_index, row in excel_file.rows.items():
            if 'sample' in row:
                try:
                    row['sample']['request'] = biosamples.encode_sample(row['sample'])
                except Exception as error:
                    error_msg = f'Encoding Error: {error}'
                    row['sample'].setdefault('errors', {}).setdefault('sample_accession', []).append(error_msg)

        biosamples_count = 0
        for row_index, row in excel_file.rows.items():
            if 'sample' in row and 'request' in row['sample']:
                try:
                    row['sample']['biosample'] = biosamples.send_sample(row['sample']['request'])
                    row['sample'].pop('request')
                    biosamples_count = biosamples_count + 1
                except Exception as error:
                    error_msg = f'BioSamples Error: {error}'
                    row['sample'].setdefault('errors', {}).setdefault('sample_accession', []).append(error_msg)
        if biosamples_count:
            excel_file.add_biosample_accessions()
            print(f'Successfully submitted {biosamples_count} BioSamples')

    close('Exiting', 0, excel_file, args)
