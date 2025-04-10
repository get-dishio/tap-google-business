"""GoogleBusiness tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_google_business import streams


class TapGoogleBusiness(Tap):
    """GoogleBusiness tap class."""

    name = "tap-google-business"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=False
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=True
        ),
        th.Property(
            "client_id",
            th.StringType,
            secret=True,
            title="Client Id",
            description="Google App Client Id.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,
            title="Client Secret",
            description="Google App Secret.",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            title="User Agent",
            description="A custom User-Agent header to send with each request.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.GoogleBusinessStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.GroupsStream(self),
            streams.UsersStream(self),
        ]


if __name__ == "__main__":
    TapGoogleBusiness.cli()
