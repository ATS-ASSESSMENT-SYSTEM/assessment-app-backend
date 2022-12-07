import base64
import json

from rest_framework.renderers import JSONRenderer
from django.conf import settings as app_settings

STATUS = app_settings.STATUS_CODES

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        key = "wjqy62fB+dwz2gyz4sMePe9u2RsMVIyuaA6wPgUeXjw="
        iv = "gNyBAsNdWQEwHvbAm8g5Jg=="
        key_in_bytes = base64.b64decode(key)
        vector_in_bytes = base64.b64decode(iv)
        cipher = AES.new(key_in_bytes, AES.MODE_CBC, vector_in_bytes)
        s = json.dumps(data)
        encrypted_data = base64.b64encode(cipher.encrypt(pad(str.encode(s), AES.block_size))).decode('utf-8')
        status_code = renderer_context["response"].status_code
        response = {
            "status": STATUS['success'],
            "data": encrypted_data,
            "message": "Successfully Retrieved"
        }

        if not str(status_code).startswith("2"):
            response["status"] = STATUS['error']
            response["data"] = None
            try:
                response["message"] = "something went wrong, trying to perform this action"
                response["error"] = data
            except KeyError:
                response['data'] = ''

        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)
