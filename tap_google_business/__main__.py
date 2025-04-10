"""GoogleBusiness entry point."""

from __future__ import annotations

from tap_google_business.tap import TapGoogleBusiness

TapGoogleBusiness.cli()
