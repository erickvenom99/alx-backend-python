# chats/middleware.py
import logging
import os
from datetime import datetime
from django.conf import settings
from django.http import HttpRequest

# Create logger
logger = logging.getLogger('request_logger')
logger.propagate = False  # Prevent double logging
logger.setLevel(logging.INFO)

# Remove all handlers to avoid duplicates on reload
if logger.handlers:
    logger.handlers.clear()

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # ENSURE LOG FILE IS CREATED IN THE CORRECT LOCATION
        log_dir = settings.BASE_DIR  # This should be your project root
        self.log_file = os.path.join(log_dir, 'requests.log')

        # Create file handler (only once)
        if not logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Optional: Also log to console during development
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)

        # Get user info
        user = request.user.email if request.user.is_authenticated else "Anonymous"

        # Create log message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - User: {user} - Path: {request.path}"

        # Log it
        logger.info(log_message)

        return response