import hashlib

from decouple import config
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    message = "Permission not granted."

    def has_permission(self, request, view):
        try:
            API_KEY = request.META['HTTP_API_KEY']
            request_ts = request.META['HTTP_REQUEST_TS']
            hash_key = request.META['HTTP_HASH_KEY']
        except KeyError as key:
            raise NotAuthenticated(
                f'Authentication credentials not provided, {key}'
            )
        local_api_key = config('API_KEY')
        local_secret_key = config('SECRET_KEY')
        try:
            if API_KEY == local_api_key:
                de_hash = local_api_key + local_secret_key + request_ts
            else:
                de_hash = None
            hash = hashlib.sha256(de_hash.encode('utf8')).hexdigest()
            print(hash)
        except:
            raise AuthenticationFailed()
        if hash_key != hash:
            raise AuthenticationFailed()
        return True
