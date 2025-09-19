from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict, List
import logging

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_storage: Dict[str, List[float]] = defaultdict(list)
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
    
    async def dispatch(self, request: Request, call_next):
        # Don't apply security headers to docs and static files
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json", "/static")):
            return await call_next(request)
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Rate limiting for authentication endpoints only
        if request.url.path in ["/api/auth/login", "/api/auth/register"]:
            client_ip = self.get_client_ip(request)
            if not self.check_rate_limit(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={
                        "http_code": 429,
                        "message": "Too many requests. Please try again later."
                    }
                )
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        minute_window = 60
        hour_window = 3600
        
        self.rate_limit_storage[client_ip] = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if current_time - timestamp < hour_window
        ]
        
        minute_requests = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if current_time - timestamp < minute_window
        ]
        
        if len(minute_requests) >= self.max_requests_per_minute:
            logging.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        if len(self.rate_limit_storage[client_ip]) >= self.max_requests_per_hour:
            logging.warning(f"Hourly rate limit exceeded for IP: {client_ip}")
            return False
        
        self.rate_limit_storage[client_ip].append(current_time)
        return True 