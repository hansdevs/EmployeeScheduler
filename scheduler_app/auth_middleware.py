"""
Authentication Middleware
Handles authentication for API requests
"""

import os
import json
from http import HTTPStatus, cookies
from typing import Dict, Optional, Any

class AuthMiddleware:
    """Middleware for handling authentication"""
    
    def __init__(self):
        """Initialize the auth middleware"""
        # Import here to avoid circular imports
        from services.user_service import UserService
        self.user_service = UserService()
    
    def process_request(self, handler) -> bool:
        """
        Process a request to check authentication
        
        Args:
            handler: The request handler
            
        Returns:
            bool: True if the request should proceed, False if it was rejected
        """
        # Skip authentication for static files and login/signup pages
        if handler.path.startswith('/pages/') or handler.path.startswith('/styles/') or \
           handler.path.startswith('/js/') or handler.path.startswith('/images/') or \
           handler.path == '/pages/signin.html' or handler.path == '/pages/getstarted.html' or \
           handler.path == '/pages/index.html' or handler.path == '/pages/about.html' or \
           handler.path == '/pages/plans.html' or handler.path.startswith('/pages/plans/'):
            return True
        
        # Skip authentication for the root path (redirects to welcome page)
        if handler.path == '/':
            return True
        
        # Skip authentication for API signup and signin
        if handler.path == '/api/signup' or handler.path == '/api/signin':
            return True
        
        # Skip authentication for fake signup and signin
        if handler.path == '/fake_signup' or handler.path == '/fake_signin':
            return True
        
        # Get the session ID from the cookie
        cookie_str = handler.headers.get('Cookie', '')
        cookie = cookies.SimpleCookie()
        cookie.load(cookie_str)
        
        if 'session_id' not in cookie:
            # No session ID, redirect to login page
            handler.send_response(HTTPStatus.FOUND)
            handler.send_header('Location', '/pages/signin.html')
            handler.end_headers()
            return False
        
        # Validate the session
        session_id = cookie['session_id'].value
        user = self.user_service.validate_session(session_id)
        
        if not user:
            # Invalid session, redirect to login page
            handler.send_response(HTTPStatus.FOUND)
            handler.send_header('Location', '/pages/signin.html')
            handler.end_headers()
            return False
        
        # Store the user in the handler for later use
        handler.user = user
        
        return True

#source control test