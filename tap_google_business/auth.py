"""GoogleBusiness Authentication."""

import json
from typing import Optional

import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.helpers._util import utc_now
from singer_sdk.streams import Stream as RESTStreamBase


class ProxyGoogleBusinessAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """API Authenticator for Proxy OAuth 2.0 flows."""

    def __init__(
        self,
        stream: RESTStreamBase,
        auth_endpoint: Optional[str] = None,
        oauth_scopes: Optional[str] = None,
        auth_headers: Optional[dict] = None,
        auth_body: Optional[dict] = None,
    ) -> None:
        """Create a new authenticator."""
        super().__init__(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes=oauth_scopes,
        )

        self._auth_headers = auth_headers
        self._auth_body = auth_body

    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`."""
        request_time = utc_now()

        token_response = requests.post(
            self.auth_endpoint,
            headers=self._auth_headers,
            data=json.dumps(self._auth_body),
        )
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json["expires_in"]
        self.last_refreshed = request_time


class GoogleBusinessAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for GoogleBusiness."""

    @property
    def oauth_request_body(self) -> dict:
        return {}
