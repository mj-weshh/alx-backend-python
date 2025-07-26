"""
Custom middleware for request logging.
Logs each incoming request with timestamp, user, and path to requests.log
"""
from datetime import datetime
import os

class RequestLoggingMiddleware:
    """
    Middleware to log all incoming requests with timestamp, user, and path.
    Logs are appended to requests.log in the project root.
    """
    def __init__(self, get_response):
        """Initialize the middleware with the next middleware in the chain."""
        self.get_response = get_response
        # Ensure the log file exists and is writable
        self.log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'requests.log')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{'='*50}\nRequest logging started at {datetime.now()}\n{'='*50}\n")

    def __call__(self, request):
        """Process the request and log it."""
        # Process the request and get the response
        response = self.get_response(request)
        
        # Log the request details
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        username = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        log_entry = f"{timestamp} - User: {username} - Path: {request.path}\n"
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return response
