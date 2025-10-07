"""
Authentication and security manager for the Calendar AI Agent.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import hashlib
import secrets
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    """Manages authentication for Google APIs and security for the agent"""

    def __init__(self, credentials_dir: str = "credentials"):
        self.credentials_dir = credentials_dir
        self.token_file = os.path.join(credentials_dir, "token.json")
        self.credentials_file = os.path.join(credentials_dir, "credentials.json")
        self.service_account_file = os.path.join(credentials_dir, "service-account.json")

        # Ensure credentials directory exists
        os.makedirs(credentials_dir, exist_ok=True)

        # Security settings
        self.session_timeout = timedelta(hours=24)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)

        self.failed_attempts = {}
        self.locked_out_until = {}

        logger.info(f"Auth manager initialized with credentials dir: {credentials_dir}")

    def setup_oauth_credentials(self, scopes: list) -> Credentials:
        """Set up OAuth2 credentials for Google APIs"""

        creds = None

        # Try to load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, scopes)
                logger.info("Loaded existing OAuth credentials")
            except Exception as e:
                logger.warning(f"Could not load existing token: {e}")

        # If there are no valid credentials available, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed OAuth credentials")
                except Exception as e:
                    logger.error(f"Could not refresh credentials: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth credentials file not found: {self.credentials_file}. "
                        "Please download it from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, scopes
                )
                creds = flow.run_local_server(port=0)
                logger.info("Obtained new OAuth credentials")

            # Save the credentials for the next run
            self._save_credentials(creds)

        return creds

    def setup_service_account_credentials(self, scopes: list) -> service_account.Credentials:
        """Set up service account credentials for Google APIs"""

        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(
                f"Service account file not found: {self.service_account_file}. "
                "Please download it from Google Cloud Console."
            )

        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=scopes
            )
            logger.info("Loaded service account credentials")
            return creds

        except Exception as e:
            logger.error(f"Could not load service account credentials: {e}")
            raise

    def _save_credentials(self, creds: Credentials):
        """Save credentials to token file securely"""
        try:
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

            # Set secure file permissions (Unix-like systems only)
            if hasattr(os, 'chmod'):
                os.chmod(self.token_file, 0o600)

            logger.info("Credentials saved securely")

        except Exception as e:
            logger.error(f"Could not save credentials: {e}")

    def validate_api_key(self, api_key: str, client_id: str) -> bool:
        """Validate API key for secure access"""

        # Check if client is locked out
        if self._is_locked_out(client_id):
            logger.warning(f"Client {client_id} is locked out")
            return False

        # Check API key format and validity
        if not api_key or len(api_key) < 32:
            self._record_failed_attempt(client_id)
            return False

        # In a real implementation, you would validate against a database
        # For now, we'll check against environment variable
        expected_key = os.getenv('API_KEY_HASH')
        if not expected_key:
            logger.warning("No API key hash configured")
            return False

        # Hash the provided key and compare
        provided_hash = self._hash_api_key(api_key)
        if provided_hash == expected_key:
            self._reset_failed_attempts(client_id)
            return True
        else:
            self._record_failed_attempt(client_id)
            return False

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    def _hash_api_key(self, api_key: str) -> str:
        """Hash an API key for secure storage"""
        salt = os.getenv('API_SALT', 'default_salt')
        return hashlib.sha256((api_key + salt).encode()).hexdigest()

    def _is_locked_out(self, client_id: str) -> bool:
        """Check if a client is locked out due to failed attempts"""
        if client_id in self.locked_out_until:
            if datetime.now() < self.locked_out_until[client_id]:
                return True
            else:
                # Lockout period expired
                del self.locked_out_until[client_id]
                self._reset_failed_attempts(client_id)

        return False

    def _record_failed_attempt(self, client_id: str):
        """Record a failed authentication attempt"""
        if client_id not in self.failed_attempts:
            self.failed_attempts[client_id] = 0

        self.failed_attempts[client_id] += 1

        if self.failed_attempts[client_id] >= self.max_failed_attempts:
            self.locked_out_until[client_id] = datetime.now() + self.lockout_duration
            logger.warning(f"Client {client_id} locked out after {self.max_failed_attempts} failed attempts")

    def _reset_failed_attempts(self, client_id: str):
        """Reset failed attempts for a client"""
        if client_id in self.failed_attempts:
            del self.failed_attempts[client_id]
        if client_id in self.locked_out_until:
            del self.locked_out_until[client_id]

    def create_secure_session(self, user_id: str) -> Dict[str, Any]:
        """Create a secure session token"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + self.session_timeout

        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'permissions': ['calendar:read', 'calendar:write']
        }

        return session_data

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token"""
        # In a real implementation, you would validate against a database
        # This is a simplified version for demonstration
        try:
            # Decode session token (this would be more complex in production)
            # For now, we'll return None to indicate invalid session
            return None

        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }

        logger.info(f"Security event: {json.dumps(log_entry)}")

        # In production, you might want to send this to a security monitoring system

    def check_rate_limit(self, client_id: str, max_requests: int = 100,
                        window_minutes: int = 60) -> bool:
        """Check if client is within rate limits"""
        # This is a simplified rate limiting implementation
        # In production, you'd use Redis or similar for distributed rate limiting

        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=window_minutes)

        # For demonstration, we'll always return True
        # In practice, you'd track requests per client per time window
        return True

    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not user_input:
            return ""

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        sanitized = user_input

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    def validate_permissions(self, session_data: Dict[str, Any],
                           required_permission: str) -> bool:
        """Validate if a session has required permissions"""
        if not session_data:
            return False

        permissions = session_data.get('permissions', [])
        return required_permission in permissions

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }