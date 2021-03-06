# Project Goals
The goal of this project is to validate metadata obtained via excel spreadsheets from the [COVID-19 Data Portal's](https://www.covid19dataportal.org/) [Drag-and-Drop Submission Tool](https://www.covid19dataportal.org/submit-data/ui-uploader/ena/) and broker the data and metadata to the appropriate archives.

*Currently* this toolset is a manual python application for Support Bioinformaticians that can validate excel spreadsheets against json schemas and broker to BioSamples, but change to the use-case over time should be expected!

# Getting Ready
## Prerequisites
 - [Python3](https://installpython3.com)
 - [Docker for Desktop](https://www.docker.com/products/docker-desktop)
    - Used for more accurate validation, *"Best Guess" Excel validation is available if you skip this prerequisite*.

## Installation
 - Get a copy of this repository on your local machine to you current directory:
    - `git clone git@github.com:ebi-ait/covid-excel-utils.git`
 - Make a new virtual environment so that this tools dependencies aren’t installed onto your main python environment:
    - `cd covid-excel-utils`
    - `python3 -m venv ./venv`
 - Activate the virtual environment:
    - `source venv/bin/activate`
 - Install dependencies
    - `python3 -m pip install -r requirements.txt`

### Updates
 - Get updates from this repository on your local machine:
    - `cd covid-excel-utils`
    - `git pull origin --ff-only`
 - Activate the virtual environment:
    - `source venv/bin/activate`
 - Update dependencies
    - `python3 -m pip install -r requirements.txt`

# Using the Tool
## Terminal Commands
- Activate the virtual environment:
    - `cd covid-excel-utils`
    - `source venv/bin/activate`
- Run the CLI:
    - `python3 ./cli.py examples/blank_v3_raw_reads.xlsx`

## Output:
The cli will add any errors in validation or submission into the original excel file as notes, styling the cells red.

### Example Console Output:
```
INFO:root:Pulling image: dockerhub.ebi.ac.uk/ait/json-schema-validator
INFO:root:Running Container: strange_gauss from image: dockerhub.ebi.ac.uk/ait/json-schema-validator
INFO:root:Validating 5 rows.
INFO:root:Removing container: strange_gauss
INFO:root:Excel file updated: examples/blank_uploader_tool_metadata_v2_raw_reads.xlsx
```
## Output Options
 - By default the `--output` parameter is set to `excel`, this will update any validation or submission errors into the passed excel file as notes, styling the cells red.
 - Set the `--output` parameter to `json` to create an output file with the same names and locations as the input excel file, with a `.json` extension. This will include the objects as loaded from the excel file, with any conversion, validation or subbmission errors listed in an `errors` attribute. If any errors are encountered they are also duplicated into an `_issues.json` for quick reference. This will not save to the original excel file.
 - Set the `--output` parameter to `all` to update the original excel file and output the json files.

## BioStudies Submissions
 - Pass the `--biostudies` parameter to submit any converted studies to BioStudies, the accession from BioStudies, will be  stored in the output file.
 - You **will** need to export the following environment variables in your terminal before running the CLI:
    - `export BIOSTUDIES_USERNAME='not_a_real_biostudies_user'`
    - `export BIOSTUDIES_PASSWORD='My very secure password'`

### BioStudies Test
 - You *can* also override the default URLs of BioStudies, this is useful for targeting the test environments.
    - `--biostudies_url http://biostudy-bia.ebi.ac.uk:8788`

## BioSamples Submissions
 - Pass the `--biosamples` parameter to submit any converted samples to BioSamples, the accession from BioSamples, will be  stored in the output file.
 - You **will** need to export the following environment variables in your terminal before running the CLI:
    - `export AAP_USERNAME='not_a_real_aap_user'`
    - `export AAP_PASSWORD='My very secure password'`
 - You *probably* need to set the `--biosamples_domain` if not present in the excel
 - `python3 ./cli.py ~/excel_file.xlsx --biosamples --biosamples_domain self.example-domain`

### BioSamples Test
 - You *can* also override the default URLs of BioSamples or AAP APIs, this is useful for targeting the test/explore environments.
    - `--biosamples_url https://wwwdev.ebi.ac.uk/biosamples`
    - `--aap_url https://explore.api.aai.ebi.ac.uk`

## Other Options
 - An up to date list of available parameters is available by running:
    - `python3 ./cli.py --help`

# Example Terminal Commands
## Installation
```
git clone git@github.com:ebi-ait/covid-excel-utils.git
cd covid-excel-utils
python3 -m venv ./venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Get updates
```
cd covid-excel-utils
git pull origin --ff-only
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Startup
```
cd covid-excel-utils
source venv/bin/activate
export AAP_USERNAME='not_a_real_aap_user'
export AAP_PASSWORD='My very secure password'
export BIOSTUDIES_USERNAME='not_a_real_biostudies_user'
export BIOSTUDIES_PASSWORD='My very secure password'
```
## Validation
```
python3 ./cli.py ~/excel_file.xlsx
```

## Output to JSON
```
python3 ./cli.py ~/excel_file.xlsx --output json
```

## Submit to BioStudies
```
python3 ./cli.py ~/excel_file.xlsx --biostudies 
```

## Submit to BioSamples
```
python3 ./cli.py ~/excel_file.xlsx \
 --biosamples \
 --biosamples_domain self.example-domain \
```

## Submit to Test BioStudies & BioSamples 
```
python3 ./cli.py ~/excel_file.xlsx \
 --output all \
 --biostudies --biostudies_url http://biostudy-bia.ebi.ac.uk:8788 \
 --biosamples --biosamples_domain self.test-domain --biosamples_url https://wwwdev.ebi.ac.uk/biosamples --aap_url https://explore.api.aai.ebi.ac.uk`
```
## Example BioStudies & BioSamples Submission Console Output (Explore/Test)
```
INFO:root:Pulling image: dockerhub.ebi.ac.uk/ait/json-schema-validator
INFO:root:Running Container: strange_gauss from image: dockerhub.ebi.ac.uk/ait/json-schema-validator
INFO:root:Removing container: strange_gauss
INFO:root:Issues detected. Continue with Brokering? (y/N)?:y
INFO:root:Attempting to Submit to BioSamples: https://wwwdev.ebi.ac.uk/biosamples, AAP: https://explore.api.aai.ebi.ac.uk
INFO:root:Attempting to Submit to BioStudies: http://biostudy-bia.ebi.ac.uk:8788
INFO:root:JSON output written to: examples/excel_file.json
INFO:root:JSON output written to: examples/excel_file_accessions.json
INFO:root:JSON output written to: examples/excel_file_issues.json
```
