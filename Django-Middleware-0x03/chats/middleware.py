# chats/middleware.py
import logging
import os
from datetime import datetime, time
from django.conf import settings
from django.http import HttpRequest, JsonResponse

# ========================
# 1. Request Logging Middleware (keep it – it works great)
# ========================
logger = logging.getLogger('request_logger')
logger.propagate = False
logger.setLevel(logging.INFO)

# Clear handlers on every reload (prevents duplicates)
if logger.handlers:
    logger.handlers.clear()

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Setup handler only once, when settings are fully loaded
        log_file = settings.BASE_DIR / 'requests.log'
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)

        user = request.user.email if request.user.is_authenticated else "Anonymous"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"{timestamp} - User: {user} - Path: {request.path}"
        logger.info(message)

        return response


# ========================
# 2. Time Restriction Middleware – FIXED VERSION
# ========================
class RestrictAccessByTimeMiddleware:
    """
    Blocks /chats and /api endpoints outside 6:00 AM – 9:00 PM
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
        # THIS IS THE ONLY CHANGE YOU NEEDED:
        # Handle both /chats and /chats/   (and /api, /api/)
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
        path = request.path.rstrip('/')

        if path.startswith('/chats') or path.startswith('/api'):
            now = datetime.now().time()
            start = time(6, 0)   # 6 AM
            end = time(21, 0)    # 9 PM

            if now < start or now >= end:
                return JsonResponse({
                    "detail": "Access to messaging is restricted outside 6:00 AM - 9:00 PM."
                }, status=403)

        # Allowed → continue to view (or 404 if no view exists – that's fine)
        return self.get_response(request)