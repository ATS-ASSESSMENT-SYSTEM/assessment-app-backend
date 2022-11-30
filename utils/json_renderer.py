import base64
import json

from rest_framework.renderers import JSONRenderer
from django.conf import settings as app_settings
STATUS = app_settings.STATUS_CODES

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        key = b"VE\xeb6:^\x9bf\xe1\x8b\x8a\xc5\xbe'\xc2\xea"
        iv = b'\xe6C\x03\xbe\xe4\x84_\xc5%g`\xd5\xfc\xcd\xd2+'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        s = json.dumps(data)
        encrypted_data = base64.b64encode(iv + cipher.encrypt(pad(str.encode(s), AES.block_size))).decode('utf-8')
        status_code = renderer_context["response"].status_code
        response = {
            "status": STATUS['success'],
            "data": data,
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
