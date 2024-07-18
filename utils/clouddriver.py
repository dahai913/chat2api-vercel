import requests
import dropbox
from dropbox.exceptions import AuthError
from utils.config import dropbox_refresh_token, dropbox_app_key, dropbox_app_secret

class DropBox:
    def __init__(self,refresh_token,key,secret):
        self.key = key
        self.secret = secret
        self.rt = refresh_token
        access_token = self.refresh_access_token()
        self.dbx = dropbox.Dropbox(access_token)

    def handle_auth_error(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except AuthError:
                access_token = self.refresh_access_token()
                self.dbx = dropbox.Dropbox(access_token)
                return func(self, *args, **kwargs)
            except Exception as e:
                raise e
        return wrapper

    @handle_auth_error
    def files_upload(self, *args, **kwargs):
        return self.dbx.files_upload(*args, **kwargs)

    @handle_auth_error
    def files_download(self, *args, **kwargs):
        return self.dbx.files_download(*args, **kwargs)

    @handle_auth_error
    def files_get_metadata(self, *args, **kwargs):
        return self.dbx.files_get_metadata(*args, **kwargs)

    def refresh_access_token(self):
        token_url = 'https://api.dropboxapi.com/oauth2/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.rt,
            'client_id': self.key,
            'client_secret': self.secret,
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()

        if 'access_token' in tokens:
            return tokens['access_token']
        else:
            raise Exception('Failed to refresh access token')
        

dbx=DropBox(dropbox_refresh_token,dropbox_app_key,dropbox_app_secret)
