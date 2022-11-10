import base64
import json
import hashlib

from django.utils.deprecation import MiddlewareMixin

from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class AESCipherMiddleware(object):

    def __init__(self):
        self.key = Random.get_random_bytes(16)

    def process_response(self, response):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        for the_key in response:
            if the_key == 'id':
                data = response.get(the_key)
                response[the_key] = base64.b64encode(
                    iv + cipher.encrypt(pad(str.encode(str(data)), AES.block_size))).decode('utf-8')
            elif type(response[the_key]) == list:
                for i in response[the_key]:
                    for j in i:
                        if j == 'id':
                            id = i.get(j)
                            i[j] = base64.b64encode(
                                iv + cipher.encrypt(pad(str.encode(str(id)), AES.block_size))).decode('utf-8')
                        elif type(i[j]) == bool:
                            d = i.get(j)
                            i[j] = base64.b64encode(
                                iv + cipher.encrypt(pad(str.encode(str(d)), AES.block_size))).decode('utf-8')
                        else:
                            i[j] = base64.b64encode(
                                iv + cipher.encrypt(pad(str.encode(i.get(j)), AES.block_size))).decode(
                                'utf-8')
            else:
                response[the_key] = base64.b64encode(
                    iv + cipher.encrypt(pad(str.encode(response.get(the_key)), AES.block_size))).decode('utf-8')
        return response

    def process_request(self, enc):
        cipher = AES.new(AES.MODE_CBC)
        ct_bytes = cipher.decrypt(unpad(AES.block_size))
        return base64.b64encode(ct_bytes)
