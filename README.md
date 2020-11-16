# Project Goals
The goal of this project is to validate metadata obtained via excel spreadsheets from the [COVID-19 Data Portal's](https://www.covid19dataportal.org/) [Drag-and-Drop Submission Tool](https://www.covid19dataportal.org/submit-data/ui-uploader/ena/) and broker the data and metadata to the appropriate archives.

*Currently* this toolset is a manual python application for Support Bioinformaticians that can validate excel spreadsheets against json schemas and broker to BioSamples, but change to the use-case over time should be expected!

# Getting Ready
## Prerequisites
 - Download and Install [Docker for Desktop](https://www.docker.com/products/docker-desktop)
 - Run this command in a terminal
 `docker pull dockerhub.ebi.ac.uk/ait/json-schema-validator`
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

# Using the Tool
## Terminal Commands
- Activate the virtual environment:
    - `cd covid-excel-utils`
    - `source venv/bin/activate`
- Run the docker validation service:
    - `docker run -p 3020:3020 -d dockerhub.ebi.ac.uk/ait/json-schema-validator`
- Run the CLI:
    - `python3 ./cli.py examples/blank_uploader_tool_metadata_v2_raw_reads.xlsx`
- When finished validating:
    - `docker stop $(docker ps -q --filter ancestor=dockerhub.ebi.ac.uk/ait/json-schema-validator)`

## Output:
The cli will create output files with the same names and locations as the input excel files, with a `.json` extension. This will include the objects as loaded from the excel file, with any conversion errors listed in an `errors` attribute. If any errors are encountered they are also duplicated into an `_issues.json` for quick reference.

## Biosamples Submissions
 - Pass the `--biosamples` parameter to submit any converted samples to BioSamples, the response from BioSamples, including the accession, will be  stored in the output file.
 - You **will** need to export the following environment variables in your terminal before running the CLI:
    - `export AAP_USERNAME='not_a_real_aap_user'`
    - `export AAP_PASSWORD='My very secure password'`
 - You *probably* need to set the `--biosamples_domain` if not present in the excel
 - `python3 ./cli.py ~/excel_file.xlsx --biosamples --biosamples_domain self.example-domain`

## Biosamples Test
 - You *can* also override the default URLs of BioSamples or AAP APIs, this is useful for targeting the test/explore versions.
    - `--biosamples_url https://wwwdev.ebi.ac.uk/biosamples`
    - `--aap_url https://explore.api.aai.ebi.ac.uk`

## Other Options
 - An up to date list of available parameters is available by running:
    - `python3 ./cli.py --help`

# Example Terminal Commands
## Installation
```
docker pull dockerhub.ebi.ac.uk/ait/json-schema-validator
git clone git@github.com:ebi-ait/covid-excel-utils.git
cd covid-excel-utils
python3 -m venv ./venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```
## Startup
```
cd covid-excel-utils
source venv/bin/activate
export AAP_USERNAME='not_a_real_aap_user'
export AAP_PASSWORD='My very secure password'
docker run -p 3020:3020 -d dockerhub.ebi.ac.uk/ait/json-schema-validator
```
## Validation
```
python3 ./cli.py ~/excel_file.xlsx
```

## Submit to BioSamples
```
python3 ./cli.py ~/excel_file.xlsx \
 --biosamples \
 --biosamples_domain self.example-domain \
```
## Submit to BioSamples Explore/Test
```
python3 ./cli.py ~/excel_file.xlsx \
 --biosamples \
 --biosamples_domain self.test-domain \
 --biosamples_url https://wwwdev.ebi.ac.uk/biosamples \
 --aap_url https://explore.api.aai.ebi.ac.uk`
```
## Shutdown
```
docker stop $(docker ps -q --filter ancestor=dockerhub.ebi.ac.uk/ait/json-schema-validator)
```
