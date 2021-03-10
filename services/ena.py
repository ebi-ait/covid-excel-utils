from datetime import date
from enum import Enum
from http import HTTPStatus
from typing import Dict, Tuple

import requests
from requests.auth import HTTPBasicAuth
from requests.models import Response


class EnaAction(Enum):
    ADD = 'ADD'
    MODIFY = 'MODIFY'
    VALIDATE = 'VALIDATE'
    VALIDATE_ADD = 'VALIDATE,ADD'
    VALIDATE_MODIFY = 'VALIDATE,MODIFY'


class Ena:
    def __init__(self, username: str, password: str, url: str = 'https://www.ebi.ac.uk/ena'):
        self.url = f"{url.rstrip('/')}/submit/drop-box/submit/"
        self.auth = HTTPBasicAuth(username, password)
    
    def submit_files(self, ena_files: Dict[str, Tuple[str, str]], action: EnaAction = None, hold_date: date = None, center: str = None):
        data = {}
        if action:
            data['ACTION'] = action.value
        if hold_date:
            data['HOLD_DATE'] = hold_date.isoformat()
        if center:
            data['CENTER_NAME'] = center
        response: Response = requests.post(self.url, auth=self.auth, data=data, files=ena_files)
        if response.status_code == HTTPStatus(200):
            return response.content
        else:
            message = f'ENA Responded with: HTTP{response.status_code}'
            error = response.json()
            if error:
                raise RuntimeError(f"{message} {error['error']} {error['message']}")
            raise RuntimeError(message)

