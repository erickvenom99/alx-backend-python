import logging
from datetime import datetime
from django.conf import settings
from models import UserSerializer
from django.http import HttpRequest

# Configure the logger to write to 'requests.log'
# Note: You can place this configuration in settings.py's LOGGING dict for larger projects,
# but for simplicity, we configure it here to write directly to a file.

logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Check if the handler already exists to prevent duplicate logs when the server reloads
if not logger.handlers:
    # Handler for writing to the requests.log file
    file_handler = logging.FileHandler(settings.BASE_DIR / 'requests.log')
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    """
    Middleware to log every request, including timestamp, user, and request path.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization goes here.
        
    def __call__(self, request: HttpRequest):
        # 1. Process the request and get the response object
        response = self.get_response(request)

        # 2. Get User Information
        # request.user is an instance of the User model (or AnonymousUser if not logged in)
        if request.user.is_authenticated:
            user = request.user.email  # Assuming your user model uses email for login
        else:
            user = "Anonymous"
        
        # 3. Format the log message
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {user} - Path: {request.path}"
        
        # 4. Log the message
        logger.info(log_message)

        # 5. Return the response
        return response