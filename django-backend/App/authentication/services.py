from django.utils.translation import gettext_lazy as _

from google.oauth2 import id_token
from google.auth.transport import requests

import logging


class google_auth_verification:

    def __init__(self, token, client_id):
        self.token = token
        self.client_id = client_id
        self.is_valid = self.is_token_verified()
    
    def is_token_verified(self):
        try:
            self.info = id_token.verify_oauth2_token(self.token, requests.Request(), self.client_id)
            return True
        except ValueError as msg:
            logging.error(msg)
            self.message = msg
            return False

