# tap-google-business

`tap-google-business` is a Singer tap for Google Business.

This fork of `tap-google-business` will sync your Google Business data under the specified `account_id`.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

To install and use this tap with Meltano:

```bash
meltano add extractor tap-google-business
```

To use standalone, you can use the following:

```bash
pip install git+https://github.com/raman-batra/tap-google-business.git
```


## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this tap is available by running:

```bash
tap-google-business --about
```

### Using Your Own Credentials

How to get these settings can be found in the following Google Business documentation:

https://developers.google.com/my-business/reference/rest/

Required settings:

- `client_id`
- `client_secret`
- `refresh_token`

Optional settings:

- `account_ids`
- `account_id`
- `start_date` (default: 90 days before the current date)
- `end_date` (default: the current date)

Config for settings that refer to a account ID should be provided as a string (e.g. `1234567890`).

#### `account_ids`/`account_id`
If `account_ids` is provided, the tap will sync get data for the corresponding accounts only. The same is true for `account_id` but for a single account. If both are provided, `account_ids` takes precedence. If neither are provided, all accounts available to the authenticated principal are synced.

### Proxy OAuth Credentials

To run the tap yourself It is highly recommended to use the [Using Your Own Credentials](#using-your-own-credentials) section listed above.

These settings for handling your credentials through a Proxy OAuth Server, these settings are used by default in a [Matatika](https://www.matatika.com/) workspace.

The benefit to using these settings in your [Matatika](https://www.matatika.com/) workspace is that you do not have to get or provide any of the OAuth credentials. All a user needs to do it allow the Matatika App permissions to access your GoogleBusiness data, and choose what `account_id` you want to get data from.

All you need to provide in your [Matatika](https://www.matatika.com/) workspace are:
- Permissions for our app to access your google account through an OAuth screen
- `account_id` (required)
- `start_date` (optional)
- `end_date` (optional)

These are not intended for a user to set manually, as such setting them could cause some config conflicts that will now allow the tap to work correctly.

Also set in by default in your [Matatika](https://www.matatika.com/) workspace environment:

- `client_id`
- `client_secret`
- `authorization_url`
- `scope`
- `access_token`
- `refresh_token`
- `refresh_proxy_url`


### Source Authentication and Authorization

## Usage

You can easily run `tap-google-business` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-google-business --version
tap-google-business --help
tap-google-business --config CONFIG --discover > ./catalog.json
```

## Developer Resources


### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_google_business/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-google-business` CLI interface directly using `poetry run`:

```bash
poetry run tap-google-business --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-google-business
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-google-business --version
# OR run a test `elt` pipeline:
meltano elt tap-google-business target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
