import threading
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication


_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None

        if user is None and get_authorization_header(request).startswith(b'Bearer'):
            jwt_authenticator = JWTAuthentication()
            try:
                validated_token = jwt_authenticator.get_validated_token(get_authorization_header(request).split()[1])
                user = jwt_authenticator.get_user(validated_token)
            except Exception:
                user = None

        _thread_locals.user = user
        response = self.get_response(request)
        return response
