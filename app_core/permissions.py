import hashlib

from decouple import config
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import BasePermission


class IsAssessmentAdminAuthenticated(BasePermission):
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
        local_api_key = config('ASSESSMENT_ADMIN_API_KEY')
        local_secret_key = config('ASSESSMENT_ADMIN_SECRET_KEY')
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
            return False
        return True


class IsAssessmentFrontendAuthenticated(BasePermission):
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
        local_api_key = config('ASSESSMENT_FRONTEND_API_KEY')
        local_secret_key = config('ASSESSMENT_FRONTEND_SECRET_KEY')
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
            return False
        return True


class IsApplicationBackendAuthenticated(BasePermission):
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
        local_api_key = config('APPLICATION_BACKEND_API_KEY')
        local_secret_key = config('APPLICATION_BACKEND_SECRET_KEY')
        try:
            if API_KEY == local_api_key:
                de_hash = local_api_key + local_secret_key + request_ts
            else:
                de_hash = None
            hash = hashlib.sha256(de_hash.encode('utf8')).hexdigest()
            print("admin", hash)
        except:
            raise AuthenticationFailed()
        if hash_key != hash:
            return False
        return True


class IsApplicationBackendOrIsAssessmentAdminAuthenticated(BasePermission):
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
        application_backend_api_key = config('APPLICATION_BACKEND_API_KEY')
        application_backend_secret_key = config('APPLICATION_BACKEND_SECRET_KEY')
        assessment_admin_api_key = config('ASSESSMENT_ADMIN_API_KEY')
        assessment_admin_secret_key = config('ASSESSMENT_ADMIN_SECRET_KEY')
        try:
            if API_KEY == application_backend_api_key:
                de_hash = application_backend_api_key + application_backend_secret_key + request_ts
            elif API_KEY == assessment_admin_api_key:
                de_hash = assessment_admin_api_key + assessment_admin_secret_key + request_ts
            else:
                de_hash = None
            hash = hashlib.sha256(de_hash.encode('utf8')).hexdigest()
            print("admin", hash)
        except:
            raise AuthenticationFailed()
        if hash_key != hash:
            return False
        return True
