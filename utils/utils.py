import base64
import json
import hashlib

from django.utils.deprecation import MiddlewareMixin

import rest_framework.parsers
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


def decrypt(data):
    b64 = json.loads(json.dumps(data))
    key = b'$\x96& \xb4"\xbc,\x88\xea\xd2\xf26\xb0f\xfe'
    iv = b'%\n\xed\xa8\xdf?Tm\xd6v\xaeW9\xf4i\xb5'
    ct = base64.b64decode(b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = unpad(cipher.decrypt(ct), AES.block_size)
    return json.loads(data.decode('utf-8'))


class CustomListCreateAPIView(ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        return super(CustomListCreateAPIView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.data.get('data'):
            data = decrypt(request.data['data'])
            request._full_data = data
            return super(CustomListCreateAPIView, self).post(request, *args, **kwargs)
        return super(CustomListCreateAPIView, self).post(request, *args, **kwargs)


class CustomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    def get(self, request, *args, **kwargs):
        return super(CustomRetrieveUpdateDestroyAPIView, self).get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if request.data.get('data'):
            data = decrypt(request.data['data'])
            request._full_data = data
            return super(CustomRetrieveUpdateDestroyAPIView, self).put(request, *args, **kwargs)
        return super(CustomRetrieveUpdateDestroyAPIView, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if request.data.get('data'):
            data = decrypt(request.data['data'])
            request._full_data = data
            return super(CustomRetrieveUpdateDestroyAPIView, self).patch(request, *args, **kwargs)
        return super(CustomRetrieveUpdateDestroyAPIView, self).patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super(CustomRetrieveUpdateDestroyAPIView, self).delete(request, *args, **kwargs)
