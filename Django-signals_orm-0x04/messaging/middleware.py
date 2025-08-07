import logging
from datetime import datetime
import os
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from collections import defaultdict, deque


class RequestLoggingMiddleware:
    """
    Middleware to log user requests to a file.
    """

    def __init__(self, get_response):
        """Initialize the middleware.
        get_response is a callable that takes a request and returns a response.
        """
        self.get_response = get_response

        # Setting up logging configuration
        log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')

        # Configure the logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)

        # Create file handler if it doen't already exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)

            # Create a formatter and set it for the handler
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(file_handler)

    def __call__(self, request):
        """Process the request ansd log the information. This method is called for each request."""

        # Get the user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        # Log the request details
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        self.logger.info(log_message)

        response = self.get_response(request)

        return response
    

class RestrictAccessByTimeMiddleware:
    """Middleware to restrict access to chat endpoint during certain hours."""

    def __init__(self, get_response):
        """Initialize  the middleware.
        get_response is a callable that takes a request and returns a response.
        """

        self.get_response = get_response

        # Define the restricted hours.
        self.start_hour = 6  # 6 AM
        self.end_hour = 21   # 9 PM

        # Define which paths to be restricted
        self.restricted_paths = [
            '/api/conversations/',
            '/api/messages/',
            '/api/chats/',
            ]

    def __call__(self, request):
        """Check if the request is within restricted hours and path."""

        # Get the current server time
        current_time = timezone.now()
        current_hour = current_time.hour

        # Check if the request path should be restricted
        if self.should_restrict_path(request.path):
            # Check if the current hour is within the restricted range
            if self.start_hour <= current_hour < self.end_hour:
                return JsonResponse(
                    {'error': 'Access to this endpoint is restricted during this time.'},
                    status=403
                )
        # If not restricted, proceed with the request
        response = self.get_response(request)
        return response
    
    def should_restrict_path(self, path):
        """Check if the request path is in the restricted paths."""
        return any(path.startswith(restricted_path) for restricted_path in self.restricted_paths)
    

class OffensiveLanguageMiddleware:
    """Middleware to limit the number of chat messages a user can sent within a 
    time window based on IP address."""

    def __init__(self, get_response):
        """Initialize the middleware with rate limiting configuration."""

        self.get_response = get_response

        # Rate limit configuration
        self.rate_limit = 5  # Maximum number of requests allowed
        self.time_window = 60  # Time window in seconds

        # Dictionary to store request timestamps for each IP address
        self.request_timestamps = defaultdict(deque)

        # Define which paths to be rate limited
        self.rate_limited_paths = [
            '/api/messages/',
            '/api/conversations/',
            '/api/chats/',
        ]

    def __call__(self, request):
        """Check if the request is within the rate limited based on 
        the IP address and time window."""

        # Only apply rate limiting to POST requests on specific paths
        if request.method == 'POST' and self.should_rate_limit(request.path):
            ip_address = self.get_client_ip(request)
            current_time = timezone.now().timestamp()

            # Clean up old timestamps
            self.request_timestamps[ip_address] = deque(
                [timestamp for timestamp in self.request_timestamps[ip_address]
                 if current_time - timestamp < self.time_window]
            )

            # Check if the rate limit has been exceeded
            if len(self.request_timestamps[ip_address]) >= self.rate_limit:
                return JsonResponse(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=429
                )

            # Record the current request timestamp
            self.request_timestamps[ip_address].append(current_time)
        
        response = self.get_response(request)
        return response


    def should_rate_limit(self, path):
        """Check if the request path is in the rate limited paths."""
        return any(path.startswith(rate_limited_path) for rate_limited_path in self.rate_limited_paths)
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    

class RolepermissionMiddleware:
    """Middleware to enforce role-based permissions for specific actions."""

    def __init__(self, get_response):
        """Initialize the middleware with role permissions configuration."""

        self.get_response = get_response

        self.admin_only_paths = [
            '/admin/',
            '/api/admin/',
        ]

        self.elevated_permission_paths = [
            '/api/conversations/',
            '/api/messages/',
            '/api/users/',
        ]

        self.public_paths = [
            '/api/token/',
            '/api/token/refresh/',
            '/api/logout/',
        ]

        self.restricted_methods = ['POST', 'PUT', 'PATCH', 'DELETE']

    def __call__(self, request):
        """Check user role and enforece permissions based on the request path and method."""

        user = request.user
        path = request.path
        method = request.method

        # Check if the user is authenticated
        if not user.is_authenticated:
            if method in self.restricted_methods and not self.is_public_path(path):
                return JsonResponse(
                    {'error': 'Authentication required.'},
                    status=401
                )

        # Check for admin-only paths
        if self.is_admin_only_path(path) and not user.is_admin():
            return JsonResponse(
                {'error': 'Admin access required.'},
                status=403
            )

        # Check for elevated permissions paths
        if self.is_elevated_permission_path(path) and not user.has_elevated_permissions():
            return JsonResponse(
                {'error': 'Elevated permissions required.'},
                status=403
            )

        response = self.get_response(request)
        return response
