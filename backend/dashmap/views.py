from django.http import JsonResponse


def root_view(request):
    """Basic root API endpoint that returns status information."""
    return JsonResponse({
        "status": "ok",
        "message": "Welcome to Dashmap!"
    })
