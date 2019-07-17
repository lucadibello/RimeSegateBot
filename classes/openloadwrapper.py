import os
import requests
import time
from openload import OpenLoad
from openload.api_exceptions import FileNotFoundException
from requests_toolbelt.multipart import encoder


class OpenloadWrapper(OpenLoad):

    def failed_conversions(self):
        pass

    def __init__(self, username: str, password: str, thumbnail_retry_delay: int):
        self.THUMBNAIL_DELAY = thumbnail_retry_delay
        super(OpenloadWrapper, self).__init__(username, password)

    def upload_large_file(self, file_path, **kwargs):
        response = self.upload_link(**kwargs)

        upload_url = response['url']
        _, file_name = os.path.split(file_path)
        with open(file_path, 'rb') as upload_file:
            data = encoder.MultipartEncoder({
                "files": (file_name, upload_file, "application/octet-stream"),
            })
        headers = {"Prefer": "respond-async", "Content-Type": data.content_type}
        response_json = requests.post(upload_url, headers=headers, data=data).json()
        self._check_status(response_json)

        return response_json['result']

    def get_thumbnail_when_ready(self, media_id):
        print("[OpenloadWrapper] Waiting {} seconds for thumbnail generation".format(self.THUMBNAIL_DELAY))
        time.sleep(self.THUMBNAIL_DELAY)
        try:
            return self.splash_image(media_id)
        except FileNotFoundException:
            print("[OpenloadWrapper] Thumbnail not ready yet")
            self.get_thumbnail_when_ready(media_id)

