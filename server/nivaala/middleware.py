import json
from django.http import JsonResponse

class JsonBodyParserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.body and request.content_type == 'application/json':
            try:
                request.data = json.loads(request.body)
            except ValueError:
                return JsonResponse({
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": "Invalid JSON payload format.",
                        "fields": {}
                    }
                }, status=400)
        return self.get_response(request)

class CentralErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and response.get('Content-Type') != 'application/json':
            return JsonResponse({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "The requested endpoint was not found.",
                    "fields": {}
                }
            }, status=404)
        return response

    def process_exception(self, request, exception):
        return JsonResponse({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exception),
                "fields": {}
            }
        }, status=500)
