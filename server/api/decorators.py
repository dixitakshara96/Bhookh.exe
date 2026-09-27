import jwt
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from .models import User

def get_authenticated_user(request):
    token = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = request.COOKIES.get('jwt_token')
        
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None

def optional_auth(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.user = get_authenticated_user(request) or type('AnonymousUser', (), {'is_authenticated': False, 'name': 'Guest Diner'})()
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def unauthorized_response(message="Authentication credentials were not provided or are invalid."):
    return JsonResponse({
        "error": {
            "code": "UNAUTHORIZED",
            "message": message,
            "fields": {}
        }
    }, status=401)

def forbidden_response(message="You do not have permission to perform this action."):
    return JsonResponse({
        "error": {
            "code": "FORBIDDEN",
            "message": message,
            "fields": {}
        }
    }, status=403)

def require_auth(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response()
        # CSRF Protection for Cookie Auth
        if request.method in ['POST', 'PUT', 'DELETE']:
            if not request.headers.get('Authorization') and request.headers.get('HX-Request') != 'true':
                return forbidden_response("CSRF Verification Failed. Missing HX-Request header.")
        request.user = user
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def require_role(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                user = get_authenticated_user(request)
                if not user:
                    return unauthorized_response()
                request.user = user
            if user.role not in allowed_roles:
                return forbidden_response(f"Requires one of the following roles: {', '.join(allowed_roles)}")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def check_ownership(user, resource_owner_id):
    """
    Returns True if user owns the resource or is admin, otherwise returns False.
    """
    if user.role == 'admin':
        return True
    return user.id == resource_owner_id
