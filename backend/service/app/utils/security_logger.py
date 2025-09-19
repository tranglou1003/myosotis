import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Create file handler for security logs
        try:
            file_handler = logging.FileHandler("logs/security.log")
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to console logging if file logging fails
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_login_attempt(self, username: str, success: bool, ip_address: str, user_agent: str = None):
        """Log login attempt"""
        event_data = {
            "event_type": "login_attempt",
            "username": username,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"Successful login: {json.dumps(event_data)}")
        else:
            self.logger.warning(f"Failed login attempt: {json.dumps(event_data)}")
    
    def log_password_change(self, user_id: int, username: str, ip_address: str):
        """Log password change"""
        event_data = {
            "event_type": "password_change",
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Password changed: {json.dumps(event_data)}")
    
    def log_account_locked(self, username: str, ip_address: str, reason: str):
        """Log account lockout"""
        event_data = {
            "event_type": "account_locked",
            "username": username,
            "ip_address": ip_address,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.warning(f"Account locked: {json.dumps(event_data)}")
    
    def log_suspicious_activity(self, event_type: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        event_data = {
            "event_type": f"suspicious_{event_type}",
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.warning(f"Suspicious activity: {json.dumps(event_data)}")
    
    def log_token_refresh(self, user_id: int, username: str, ip_address: str):
        """Log token refresh"""
        event_data = {
            "event_type": "token_refresh",
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Token refreshed: {json.dumps(event_data)}")
    
    def log_logout(self, user_id: int, username: str, ip_address: str):
        """Log user logout"""
        event_data = {
            "event_type": "logout",
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"User logged out: {json.dumps(event_data)}")

security_logger = SecurityLogger() 