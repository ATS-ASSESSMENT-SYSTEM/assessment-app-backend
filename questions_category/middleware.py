import base64
import json
import hashlib

from django.utils.deprecation import MiddlewareMixin

import rest_framework.parsers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class AESCipherMiddleware(MiddlewareMixin):

    # def __init__(self):
    #     self.key = Random.get_random_bytes(16)

    def process_response(self, request, response):
        key = b"VE\xeb6:^\x9bf\xe1\x8b\x8a\xc5\xbe'\xc2\xea"
        iv = b'\xe6C\x03\xbe\xe4\x84_\xc5%g`\xd5\xfc\xcd\xd2+'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        print(response)
        print(vars(response))
        print(response.data)
        s = json.dumps(response.data)
        r = base64.b64encode(iv + cipher.encrypt(pad(str.encode(s), AES.block_size))).decode('utf-8')
        response = Response({'data': r})
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response
        # print(vars(response))
        # print(response.data)
        # if response.data.get('results'):
        #     for dat in response.data['results']:
        #         for the_key in dat:
        #             if type(dat[the_key]) == int:
        #                 data = dat.get(the_key)
        #                 dat[the_key] = base64.b64encode(
        #                     iv + cipher.encrypt(pad(str.encode(str(data)), AES.block_size))).decode('utf-8')
        #
        #             elif type(dat[the_key]) == list:
        #                 for i in dat[the_key]:
        #                     for j in i:
        #                         if type(i[j]) == int:
        #                             id = i.get(j)
        #                             i[j] = base64.b64encode(
        #                                 iv + cipher.encrypt(pad(str.encode(str(id)), AES.block_size))).decode('utf-8')
        #                         elif type(i[j]) == bool:
        #                             d = i.get(j)
        #                             i[j] = base64.b64encode(
        #                                 iv + cipher.encrypt(pad(str.encode(str(d)), AES.block_size))).decode('utf-8')
        #                         else:
        #                             i[j] = base64.b64encode(
        #                                 iv + cipher.encrypt(pad(str.encode(i.get(j)), AES.block_size))).decode(
        #                                 'utf-8')
        #             else:
        #                 dat[the_key] = base64.b64encode(
        #                     iv + cipher.encrypt(pad(str.encode(dat.get(the_key)), AES.block_size))).decode('utf-8')
        #     print(response.data)
        #     response.data['X-My-Header'] = request.META
        #     return response
        # else:
        #     for data in response.data:
        #         if type(response.data[data]) == int:
        #             id = response.data.get(data)
        #             response.data[data] = base64.b64encode(
        #                 iv + cipher.encrypt(pad(str.encode(str(id)), AES.block_size))).decode('utf-8')
        #         elif type(response.data[data]) == type(None):
        #             s = response.data.get(data)
        #             response.data[data] = base64.b64encode(
        #                 iv + cipher.encrypt(pad(str.encode(str(s)), AES.block_size))).decode('utf-8')
        #         else:
        #             response.data[data] = base64.b64encode(
        #                 iv + cipher.encrypt(pad(str.encode(response.data.get(data)), AES.block_size))).decode('utf-8')
        #     print(response.data)
        #     print(vars(response))
        #     return Response(response)

    # def process_request(self, enc):
    #     key = b"VE\xeb6:^\x9bf\xe1\x8b\x8a\xc5\xbe'\xc2\xea"
    #     cipher = AES.new(AES.MODE_CBC)
    #     ct_bytes = cipher.decrypt(unpad(AES.block_size))
    #     return base64.b64encode(ct_bytes)


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        key = Random.get_random_bytes(16)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        print(response)
        print(response.data)
        for data in response.data:
            if type(response.data[data]) == int:
                id = response.data.get(data)
                response.data[data] = base64.b64encode(
                    iv + cipher.encrypt(pad(str.encode(str(id)), AES.block_size))).decode('utf-8')
            elif type(response.data[data]) == type(None):
                s = response.data.get(data)
                response.data[data] = base64.b64encode(
                    iv + cipher.encrypt(pad(str.encode(str(s)), AES.block_size))).decode('utf-8')
            else:
                response.data[data] = base64.b64encode(
                    iv + cipher.encrypt(pad(str.encode(response.data.get(data)), AES.block_size))).decode('utf-8')
        print(response.data)

        # Code to be executed for each request/response after
        # the view is called.

        return response.data
