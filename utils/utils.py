import base64
import json
import hashlib

from decouple import config
from django.utils.deprecation import MiddlewareMixin

import rest_framework.parsers
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


def decrypt(data):
    b64 = json.loads(json.dumps(data))
    key = config('KEY')
    iv = config('IV')
    key_in_bytes = base64.b64decode(key)
    vector_in_bytes = base64.b64decode(iv)
    ct = base64.b64decode(b64)
    cipher = AES.new(key_in_bytes, AES.MODE_CBC, vector_in_bytes)
    data = unpad(cipher.decrypt(ct), AES.block_size)
    return json.loads(data.decode('utf-8'))


class CustomListCreateAPIView(ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        return super(CustomListCreateAPIView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                return super(CustomListCreateAPIView, self).post(request, *args, **kwargs)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)


class CustomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    def get(self, request, *args, **kwargs):
        return super(CustomRetrieveUpdateDestroyAPIView, self).get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                return super(CustomRetrieveUpdateDestroyAPIView, self).put(request, *args, **kwargs)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        if request.data.get('data'):
            try:
                data = decrypt(request.data['data'])
                request._full_data = data
                return super(CustomRetrieveUpdateDestroyAPIView, self).patch(request, *args, **kwargs)
            except ValueError:
                return Response('Padding incorrect, Encryption and Decryption key and vector must be same.',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Data must be encrypted', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return super(CustomRetrieveUpdateDestroyAPIView, self).delete(request, *args, **kwargs)
