import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

log = logging.getLogger(__name__)


class ResponseLoggingMiddleware(MiddlewareMixin):
    req = None

    def basicConfig(self, **messages):

        with open(file='app_core.log', mode='a') as file:
            handler = file.write(
                f'Time: {messages["time"]}' + "  "
                f'Method:{self.req.method}' + "  "
                f'Status_code:{messages["method"]}' + " "
                f"Endpoint: {messages['endpoint']}\n"
            )

            return handler

    def process_response(self, request, response):
        self.req = request
        try:

            log.info(self.basicConfig(
                time=timezone.now(),
                filename="app_core.log",
                method=f'{response.status_code}',
                endpoint=f"{request.META['REMOTE_ADDR']}"
                         f"{request.get_full_path()}"
            ))
        except Exception as e:
            log.error(f'RequestLoggingMiddleware error : {e}')

        return response