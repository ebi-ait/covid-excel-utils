from typing import Dict, Set

import boto3

from submission.entity import Entity
from submission.submission import Submission
from .base import BaseValidator

ENDPOINT = 'https://s3.embassy.ebi.ac.uk'
REGION = 'eu-west-2'
BUCKET = 'covid-utils-ui-88560523'


class UploadValidator(BaseValidator):
    def __init__(self, folder_uuid:str):
        self.file_manifest = self.get_file_manifest(folder_uuid)

    def validate_data(self, data: Submission):
        for entity in data.get_entities('run_experiment'):
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
        else:
            entity.attributes[check_attribute] = upload_checksum

    @staticmethod
    def get_file_manifest(folder_uuid: str) -> Dict[str, str]:
        path = f'{folder_uuid}/'
        manifest = {}
        for key in UploadValidator.__get_file_keys(path):
            if '.xlsx.' not in key.lower():
                file_name_checksum = key.partition(path)[2].rpartition('.')
                manifest[file_name_checksum[0]] = file_name_checksum[2]
        return manifest

    @staticmethod
    def __get_file_keys(path: str) -> Set[str]:
        keys = set()
        s3 = boto3.resource('s3', endpoint_url=ENDPOINT, region_name=REGION)
        bucket = s3.Bucket(BUCKET)
        for obj in bucket.objects.filter(Prefix=path):
            if obj.key != path:
                keys.add(obj.key)
        return keys
