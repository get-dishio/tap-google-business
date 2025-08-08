"""Utilities used in this module"""

from singer_sdk._singerlib import Catalog
from singer_sdk.helpers._catalog import (
    deselect_all_streams,
    set_catalog_stream_selected,
)

from tap_google_business.tap import TapGoogleBusiness

ACCOUNTS_RESPONSE = {
    "name": "accounts/12345",
    "accountName": "Test Account",
    "type": "PERSONAL",
    "verificationState": "VERIFIED",
    "vettedState": "NOT_VETTED",
}

SINGER_MESSAGES = []


def accumulate_singer_messages(_, message):
    """function to collect singer library write_message in tests"""
    SINGER_MESSAGES.append(message)


def set_up_tap_with_custom_catalog(mock_config, stream_list):
    tap = TapGoogleBusiness(config=mock_config)
    # Run discovery
    tap.run_discovery()
    # Get catalog from tap
    catalog = Catalog.from_dict(tap.catalog_dict)
    # Reset and re-initialize with an input catalog
    deselect_all_streams(catalog=catalog)
    for stream in stream_list:
        set_catalog_stream_selected(
            catalog=catalog,
            stream_name=stream,
            selected=True,
        )
    # Initialise tap with new catalog
    return TapGoogleBusiness(config=mock_config, catalog=catalog.to_dict())
