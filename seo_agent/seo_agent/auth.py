"""OAuth authentication handler for Google APIs"""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from . import config


class GoogleAuthManager:
    """Manages OAuth authentication for Google Analytics and Search Console"""

    def __init__(self, scopes=None):
        """
        Initialize the authentication manager

        Args:
            scopes: List of OAuth scopes to request. Defaults to all scopes.
        """
        self.scopes = scopes or config.ALL_SCOPES
        self.credentials = None
        self.token_file = config.TOKEN_FILE
        self.credentials_file = config.CREDENTIALS_FILE

    def get_credentials(self):
        """
        Get valid credentials, refreshing or creating new ones if necessary

        Returns:
            google.oauth2.credentials.Credentials: Valid credentials
        """
        # Check if we have stored credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)

        # If credentials are not valid, refresh or create new ones
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # Refresh expired credentials
                self.credentials.refresh(Request())
            else:
                # Create new credentials through OAuth flow
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth credentials file not found at {self.credentials_file}. "
                        "Please download it from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    self.scopes
                )
                self.credentials = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)

        return self.credentials

    def clear_credentials(self):
        """Clear stored credentials"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            self.credentials = None


# Global authentication manager instance
auth_manager = GoogleAuthManager()


def get_credentials():
    """Convenience function to get credentials"""
    return auth_manager.get_credentials()
