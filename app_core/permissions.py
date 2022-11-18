from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class RequestPermission(BasePermission):
    message = "Permission not granted."
    
    def has_permission(self, request, view):
        try:
            api_key = request.META.get('HTTP_API_KEY')
            hash_key = request.META.get('HTTP_HASH_KEY')
            request_time_stamp = request.META.get('HTTP_REQEUST_TS')
        except:
            raise AuthenticationFailed('api_key or hash_key or request time stamp is not provided.')
