"""Stream type classes for tap-google-business."""

from pathlib import Path
from typing import Iterable, Optional, Any, Dict

from singer_sdk import typing as th
from tap_google_business.client import GoogleBusinessStream, GoogleBusinessPerformanceStream

class AccountsStream(GoogleBusinessStream):
    """Accounts stream."""

    name = "accounts"
    path = "/accounts"
    primary_keys = ["name"]
    records_jsonpath = "$.accounts[*]"

    def parse_response(self, response: "requests.Response") -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        if response.json().get("accounts"):
            yield from response.json()["accounts"]
        else:
            yield response.json()

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-like dictionary objects."""
        if self.config.get("account_ids"):
            for account_id in self.config["account_ids"]:
                self.path = f"/accounts/{account_id}"
                yield from super().get_records(context)
        else:
            yield from super().get_records(context)

    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("accountName", th.StringType),
        th.Property("primaryOwner", th.StringType),
        th.Property("type", th.StringType),
        th.Property("role", th.StringType),
        th.Property("verificationState", th.StringType),
        th.Property("vettedState", th.StringType),
        th.Property("accountNumber", th.StringType),
        th.Property("permissionLevel", th.StringType),
        th.Property("organizationInfo", th.ObjectType(
            th.Property("registeredDomain", th.StringType),
            th.Property("address", th.ObjectType(
                th.Property("revision", th.IntegerType),
                th.Property("regionCode", th.StringType),
                th.Property("languageCode", th.StringType),
                th.Property("postalCode", th.StringType),
                th.Property("sortingCode", th.StringType),
                th.Property("administrativeArea", th.StringType),
                th.Property("locality", th.StringType),
                th.Property("sublocality", th.StringType),
                th.Property("addressLines", th.ArrayType(th.StringType)),
                th.Property("recipients", th.ArrayType(th.StringType)),
                th.Property("organization", th.StringType),
            )),
            th.Property("phoneNumber", th.StringType),
        )),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "account_name": record["name"]
        }

class AccountAdminsStream(GoogleBusinessStream):
    """Account Admins stream."""

    name = "account_admins"
    parent_stream_type = AccountsStream
    path = "/{account_name}/admins"
    primary_keys = ["name"]
    records_jsonpath = "$.accountAdmins[*]"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("admin", th.StringType),
        th.Property("account", th.StringType),
        th.Property("role", th.StringType),
        th.Property("pendingInvitation", th.BooleanType),
    ).to_dict()

class LocationsStream(GoogleBusinessStream):
    """Locations stream."""

    name = "locations"
    parent_stream_type = AccountsStream
    path = "/{account_name}/locations"
    primary_keys = ["name"]
    records_jsonpath = "$.locations[*]"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("languageCode", th.StringType),
        th.Property("storeCode", th.StringType),
        th.Property("title", th.StringType),
        th.Property("phoneNumbers", th.ObjectType(
            th.Property("primaryPhone", th.StringType),
            th.Property("additionalPhones", th.ArrayType(th.StringType)),
        )),
        th.Property("categories", th.ObjectType(
            th.Property("primaryCategory", th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("displayName", th.StringType),
            )),
            th.Property("additionalCategories", th.ArrayType(th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("displayName", th.StringType),
            ))),
        )),
        th.Property("storefrontAddress", th.ObjectType(
            th.Property("revision", th.IntegerType),
            th.Property("regionCode", th.StringType),
            th.Property("languageCode", th.StringType),
            th.Property("postalCode", th.StringType),
            th.Property("sortingCode", th.StringType),
            th.Property("administrativeArea", th.StringType),
            th.Property("locality", th.StringType),
            th.Property("sublocality", th.StringType),
            th.Property("addressLines", th.ArrayType(th.StringType)),
            th.Property("recipients", th.ArrayType(th.StringType)),
            th.Property("organization", th.StringType),
        )),
        th.Property("websiteUri", th.StringType),
        th.Property("labels", th.ArrayType(th.StringType)),
        th.Property("latlng", th.ObjectType(
            th.Property("latitude", th.NumberType),
            th.Property("longitude", th.NumberType),
        )),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "location_name": record["name"]
        }

class LocationAdminsStream(GoogleBusinessStream):
    """Location Admins stream."""

    name = "location_admins"
    parent_stream_type = LocationsStream
    path = "/{location_name}/admins"
    primary_keys = ["name"]
    records_jsonpath = "$.admins[*]"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("admin", th.StringType),
        th.Property("account", th.StringType),
        th.Property("role", th.StringType),
        th.Property("pendingInvitation", th.BooleanType),
    ).to_dict()

class MultiDailyMetricsTimeSeriesStream(GoogleBusinessPerformanceStream):
    """Multi Daily Metrics Time Series stream."""

    name = "multi_daily_metrics_time_series"
    parent_stream_type = LocationsStream
    path = "/{location_name}:fetchMultiDailyMetricsTimeSeries"
    primary_keys = ["location_name"]
    records_jsonpath = "$.multiDailyMetricTimeSeries[*]"
    schema = th.PropertiesList(
        th.Property("dailyMetricTimeSeries", th.ArrayType(th.ObjectType(
            th.Property("dailyMetric", th.StringType),
            th.Property("dailySubEntityType", th.ObjectType(
                th.Property("dayOfWeek", th.StringType),
                th.Property("timeOfDay", th.ObjectType(
                    th.Property("hours", th.IntegerType),
                    th.Property("minutes", th.IntegerType),
                    th.Property("seconds", th.IntegerType),
                    th.Property("nanos", th.IntegerType),
                )),
            )),
            th.Property("timeSeries", th.ObjectType(
                th.Property("datedValues", th.ArrayType(th.ObjectType(
                    th.Property("date", th.ObjectType(
                        th.Property("year", th.IntegerType),
                        th.Property("month", th.IntegerType),
                        th.Property("day", th.IntegerType),
                    )),
                    th.Property("value", th.StringType),
                ))),
            )),
        ))),
    ).to_dict()

class DailyMetricsTimeSeriesStream(GoogleBusinessPerformanceStream):
    """Daily Metrics Time Series stream."""

    name = "daily_metrics_time_series"
    parent_stream_type = LocationsStream
    path = "/{location_name}:getDailyMetricsTimeSeries"
    primary_keys = ["location_name"]
    records_jsonpath = "$.timeSeries"
    schema = th.PropertiesList(
        th.Property("datedValues", th.ArrayType(th.ObjectType(
            th.Property("date", th.ObjectType(
                th.Property("year", th.IntegerType),
                th.Property("month", th.IntegerType),
                th.Property("day", th.IntegerType),
            )),
            th.Property("value", th.StringType),
        ))),
    ).to_dict()

class SearchKeywordsImpressionsMonthlyStream(GoogleBusinessPerformanceStream):
    """Search Keywords Impressions Monthly stream."""

    name = "search_keywords_impressions_monthly"
    parent_stream_type = LocationsStream
    path = "/{location_name}/searchkeywords/impressions/monthly"
    primary_keys = ["location_name"]
    records_jsonpath = "$.searchKeywordsCounts[*]"
    schema = th.PropertiesList(
        th.Property("searchKeyword", th.StringType),
        th.Property("insightsValue", th.ObjectType(
            th.Property("value", th.StringType),
            th.Property("threshold", th.StringType),
        )),
    ).to_dict()
