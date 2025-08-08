"""Tests the tap using a mock proxy oauth config."""

import unittest

import responses
import singer_sdk._singerlib as singer

import tests.utils as test_utils
from tap_google_business.tap import TapGoogleBusiness


class TestTapGoogleBusinessWithProxyOAuthCredentials(unittest.TestCase):
    """Test class for tap-google-business using proxy refresh credentials"""

    def setUp(self):
        self.mock_config = {
            "refresh_proxy_url": "http://localhost:8080/api/tokens/oauth2-google/token",
            "refresh_proxy_url_auth": "Bearer proxy_url_token",
            "refresh_token": "1234",
            "account_id": "1234567890",
        }
        responses.reset()
        del test_utils.SINGER_MESSAGES[:]
        TapGoogleBusiness.write_message = test_utils.accumulate_singer_messages

    def test_proxy_oauth_discovery(self):
        """Test basic discover sync with proxy refresh credentials"""

        catalog = TapGoogleBusiness(config=self.mock_config).discover_streams()

        # Assert the correct number of default streams found
        self.assertEqual(len(catalog), 4, "Total streams from default catalog")

    @responses.activate
    def test_proxy_oauth_refresh(self):
        """Test proxy oauth refresh"""

        tap = test_utils.set_up_tap_with_custom_catalog(
            self.mock_config, ["accounts"]
        )

        responses.add(
            responses.POST,
            "http://localhost:8080/api/tokens/oauth2-google/token",
            json={"access_token": "refresh_token_updated", "expires_in": 3622},
            status=200,
        )

        responses.add(
            responses.GET,
            "https://mybusinessaccountmanagement.googleapis.com/v1/accounts/1234567890",
            json=test_utils.ACCOUNTS_RESPONSE,
            status=200,
        )

        tap.sync_all()

        # Assert first oauth token call is using pre set refresh_proxy_url_auth

        oauth_refresh_request_token = responses.calls[0].request.headers[
            "Authorization"
        ]

        self.assertEqual(oauth_refresh_request_token, "Bearer proxy_url_token")

        # Assert that returned refresh token is used in the call.

        accounts_request_token = responses.calls[1].request.headers[
            "Authorization"
        ]

        self.assertEqual(
            accounts_request_token, "Bearer refresh_token_updated"
        )

        # Assert that messages are output from sync (its actually working).
        self.assertEqual(len(test_utils.SINGER_MESSAGES), 3)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[0], singer.SchemaMessage)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[1], singer.RecordMessage)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[2], singer.StateMessage)
