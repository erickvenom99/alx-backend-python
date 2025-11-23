# chats/middleware.py
import logging
import os
from datetime import datetime, time
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

_IP_MESSAGE_HISTORY = defaultdict(list)
MAX_MESSAGES = 5        # Max messages allowed
TIME_WINDOW = 60

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


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Rate limits message sending: 5 messages per minute per IP address
    Task requires this class name exactly → OffensiveLanguageMiddleware
    """
    def __call__(self, request):
        # Only apply to POST requests on message-related paths
        if (request.method == "POST" and 
            request.path.startswith(('/chats/', '/api/', '/messages/'))):
            
            ip = self.get_client_ip(request)
            
            now = time.time()
            one_minute_ago = now - TIME_WINDOW

            # Clean old messages outside the time window
            if ip in _IP_MESSAGE_HISTORY:
                _IP_MESSAGE_HISTORY[ip] = [
                    timestamp for timestamp in _IP_MESSAGE_HISTORY[ip]
                    if timestamp > one_minute_ago
                ]
            else:
                _IP_MESSAGE_HISTORY[ip] = []

            # Check if limit exceeded
            if len(_IP_MESSAGE_HISTORY[ip]) >= MAX_MESSAGES:
                return JsonResponse({
                    "detail": "Rate limit exceeded. You can only send 5 messages per minute."
                }, status=429)  # 429 Too Many Requests

            # Allow request and record this message
            _IP_MESSAGE_HISTORY[ip].append(now)

        # Allow request to continue
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get real IP even behind proxy"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

class RolepermissionMiddleware(MiddlewareMixin):
    """
    Blocks access to admin-only paths if user is not admin or moderator
    ALX expects exact class name: RolepermissionMiddleware (no space)
    """
    def __call__(self, request):
        # Define admin-only paths
        admin_paths = [
            '/admin/',
            '/chats/admin/',
            '/api/admin/',
            '/chats/delete/',      # example
            '/chats/ban/',         # example
        ]

        # Check if current path requires admin role
        if any(request.path.startswith(path) for path in admin_paths):
            user = request.user

            # Allow unauthenticated users to reach login page
            if not user.is_authenticated:
                return JsonResponse({
                    "detail": "Authentication required for admin access."
                }, status=403)

            # Check user's role from your custom User model
            # Adjust this line based on your User.role field
            user_role = getattr(user, 'role', 'guest').lower()

            if user_role not in ['admin', 'moderator']:
                return JsonResponse({
                    "detail": "You do not have permission to perform this action."
                }, status=403)

        # Allow normal access
        response = self.get_response(request)
        return response