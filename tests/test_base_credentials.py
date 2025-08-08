"""Tests the tap using a mock base credentials config."""

import unittest

import responses
import singer_sdk._singerlib as singer

import tests.utils as test_utils
from tap_google_business.tap import TapGoogleBusiness


class TestTapGoogleBusinessWithBaseCredentials(unittest.TestCase):
    """Test class for tap-google-business using base credentials"""

    def setUp(self):
        self.mock_config = {
            "client_id": "1234",
            "client_secret": "1234",
            "refresh_token": "1234",
            "account_id": "1234567890",
        }
        responses.reset()
        del test_utils.SINGER_MESSAGES[:]

        TapGoogleBusiness.write_message = test_utils.accumulate_singer_messages

    def test_base_credentials_discovery(self):
        """Test basic discover sync with Bearer Token"""

        catalog = TapGoogleBusiness(config=self.mock_config).discover_streams()

        # expect valid catalog to be discovered
        self.assertEqual(len(catalog), 4, "Total streams from default catalog")

    @responses.activate
    def test_google_business_sync_accounts(self):
        """Test sync."""

        tap = test_utils.set_up_tap_with_custom_catalog(
            self.mock_config, ["accounts"]
        )

        responses.add(
            responses.POST,
            "https://www.googleapis.com/oauth2/v4/token?refresh_token=1234&client_id=1234"
            + "&client_secret=1234&grant_type=refresh_token",
            json={"access_token": 12341234, "expires_in": 3622},
            status=200,
        )

        responses.add(
            responses.GET,
            "https://mybusinessaccountmanagement.googleapis.com/v1/accounts/1234567890",
            json=test_utils.ACCOUNTS_RESPONSE,
            status=200,
        )

        tap.sync_all()

        self.assertEqual(len(test_utils.SINGER_MESSAGES), 3)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[0], singer.SchemaMessage)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[1], singer.RecordMessage)
        self.assertIsInstance(test_utils.SINGER_MESSAGES[2], singer.StateMessage)
