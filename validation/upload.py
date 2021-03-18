import logging
from contextlib import closing
import io
from typing import Dict

import boto3

from submission.entity import Entity
from submission.submission import Submission
from .base import BaseValidator

ENDPOINT = 'https://s3.embassy.ebi.ac.uk'
REGION = 'eu-west-2'
BUCKET = 'covid-utils-ui-88560523'
MANIFEST_FILE_NAME = 'data_file_manifest'


class UploadValidator(BaseValidator):
    def __init__(self, folder_uuid: str):
        self.folder_uuid = folder_uuid
        self.file_manifest = self.get_manifest(folder_uuid)

    def validate_data(self, data: Submission):
        entities = data.get_entities('run_experiment')
        logging.info(f'Validating file checksums for {len(entities)} run(s)')
        for entity in entities:
            self.validate_entity(entity)

    def validate_entity(self, entity: Entity):
        file_number = 1
        while True:
            file_attribute = f'uploaded_file_{file_number}'
            check_attribute = file_attribute + '_checksum'
            if file_attribute not in entity.attributes:
                break
            self.validate_file(entity, file_attribute, check_attribute)
            file_number = file_number + 1

    def validate_file(self, entity: Entity, file_attribute: str, check_attribute: str):
        file_name = entity.attributes[file_attribute]
        if file_name not in self.file_manifest:
            entity.add_error(file_attribute, f'File has not been uploaded to drag-and-drop: {file_name}')
            return
        upload_checksum = self.file_manifest[file_name]
        if check_attribute in entity.attributes:
            stated_checksum = entity.attributes[check_attribute]
            if stated_checksum != upload_checksum:
                entity.add_error(check_attribute, f'The checksum found on drag-and-drop {upload_checksum} does not match: {stated_checksum}')
                return
        else:
            entity.attributes[check_attribute] = upload_checksum
    
    @staticmethod
    def get_manifest(folder_uuid: str) -> Dict[str, str]:
        manifest_text = UploadValidator.get_manifest_file(f'{folder_uuid}/{MANIFEST_FILE_NAME}')
        manifest = {}
        for line in manifest_text.splitlines():
            file_name, comma, file_checksum = line.strip().partition(',')
            manifest[file_name] = file_checksum
        return manifest
    
    @staticmethod
    def get_manifest_file(file_key: str) -> str:
        with closing(io.BytesIO()) as manifest_file:
            s3 = boto3.client('s3', endpoint_url=ENDPOINT, region_name=REGION)
            s3.download_fileobj(BUCKET, file_key, manifest_file)
            return manifest_file.getvalue().decode("utf-8") 
