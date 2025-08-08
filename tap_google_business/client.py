"""REST client handling, including GoogleBusinessStream base class."""

from backports.cached_property import cached_property
from typing import Any, Dict, Optional

import requests
from singer_sdk.authenticators import OAuthAuthenticator
from singer_sdk.streams import RESTStream

from tap_google_business.auth import GoogleBusinessAuthenticator, ProxyGoogleBusinessAuthenticator


class ResumableAPIError(Exception):
    def __init__(self, message: str, response: requests.Response) -> None:
        super().__init__(message)
        self.response = response


class GoogleBusinessStream(RESTStream):
    """GoogleBusiness stream class."""

    url_base = "https://mybusinessaccountmanagement.googleapis.com/v1"
    records_jsonpath = "$[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.nextPageToken"  # Or override `get_next_page_token`.
    _LOG_REQUEST_METRIC_URLS: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.config.get("account_id"):
            self._config["account_ids"] = [self.config.get("account_id")]
        elif self.config.get("account_ids"):
            self._config["account_ids"] = self.config.get("account_ids").split(",")

    def response_error_message(self, response: requests.Response) -> str:
        """Build error message for invalid http statuses."""
        base_msg = super().response_error_message(response)
        try:
            error = response.json()["error"]
            main_message = (
                f"Error {error['code']}: {error['message']} ({error['status']})"
            )

            if "details" in error and error["details"]:
                detail = error["details"][0]
                if "errors" in detail and detail["errors"]:
                    error_detail = detail["errors"][0]
                    detailed_message = error_detail.get("message", "")
                    request_id = detail.get("requestId", "")

                    return f"{base_msg}. {main_message}\nDetails: {detailed_message}\nRequest ID: {request_id}"

            return base_msg + main_message
        except Exception:
            return base_msg

    @cached_property
    def authenticator(self) -> OAuthAuthenticator:
        """Return a new authenticator object."""
        base_auth_url = "https://www.googleapis.com/oauth2/v4/token"

        client_id = self.config.get("client_id", None)
        client_secret = self.config.get("client_secret", None)
        refresh_token = self.config.get("refresh_token", None)

        auth_url = f"{base_auth_url}?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token"

        if client_id and client_secret and refresh_token:
            return GoogleBusinessAuthenticator(stream=self, auth_endpoint=auth_url)

        auth_body = {
            "refresh_token": self.config.get("refresh_token"),
            "grant_type": "refresh_token",
        }

        auth_headers = {
            "authorization": self.config.get("refresh_proxy_url_auth"),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        return ProxyGoogleBusinessAuthenticator(
            stream=self,
            auth_endpoint=self.config.get("refresh_proxy_url"),
            auth_body=auth_body,
            auth_headers=auth_headers,
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["pageToken"] = next_page_token
        return params

    def get_records(self, context):
        try:
            yield from super().get_records(context)
        except ResumableAPIError as e:
            self.logger.warning(e)

class GoogleBusinessPerformanceStream(GoogleBusinessStream):
    """GoogleBusinessPerformance stream class."""

    url_base = "https://businessprofileperformance.googleapis.com/v1"
