import base64
import json

from rest_framework.renderers import JSONRenderer
from django.conf import settings as app_settings

STATUS = app_settings.STATUS_CODES

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        key = b'$\x96& \xb4"\xbc,\x88\xea\xd2\xf26\xb0f\xfe'
        iv = b'%\n\xed\xa8\xdf?Tm\xd6v\xaeW9\xf4i\xb5'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        d = {
            "question_text": "Question 2034",
            "question_type": "Multi-choice",
            "question_category": "Real",
            "choices": [
                {
                    "id": 63,
                    "choice_text": "C",
                    "is_correct": True
                },
                {
                    "id": 64,
                    "choice_text": "B",
                    "is_correct": False
                }
            ]
        }
        s = json.dumps(d)
        encrypted_data = base64.b64encode(cipher.encrypt(pad(str.encode(s), AES.block_size))).decode('utf-8')
        print("data", encrypted_data)
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
