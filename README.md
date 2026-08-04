# Pango Parking

<p align="center">
   <img src="assets/logo.svg" alt="Pango Parking logo" width="140" />
</p>

[![HACS Default](https://img.shields.io/badge/HACS-Default-31A9F4.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/erezdaniel7/pango_parking_integration.svg?style=for-the-badge&color=blue)](https://github.com/erezdaniel7/pango_parking_integration/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.6+-blue.svg?style=for-the-badge)](https://www.home-assistant.io/)

A [Home Assistant](https://www.home-assistant.io/) integration that monitors your active parking sessions from [Pango](https://www.pango.co.il/) (Israel).

## Features

- 🚗 Real-time parking status (active / inactive)
- ⏱️ Parking start and end times
- 🔄 Configurable polling interval (default: 10 minutes)
- 🔑 Automatic session management and re-login
- 📢 Automation blueprint for parking notifications
- 🔘 Manual refresh button

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| Is parking active | Binary sensor | `on` when parking is active |
| Parking start time | Sensor | Timestamp when parking started |
| Parking end time | Sensor | Timestamp when parking ends |
| Telemetry last updated | Sensor | Last successful data fetch from Pango |
| Poll now | Button | Trigger an immediate data refresh |

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=erezdaniel7&repository=pango_parking_integration&category=Integration)

1. Search for **Pango Parking** in HACS.
2. Click **Download**.
3. Restart Home Assistant.

### Manual

1. Download `pango_parking.zip` from the [latest release](https://github.com/erezdaniel7/pango_parking_integration/releases).
2. Extract and copy `pango_parking/` to your `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

After installation, add the integration via the UI:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pango_parking)

Or manually: **Settings → Devices & Services → Add Integration → Pango Parking**

| Parameter | Description | Default |
|-----------|-------------|---------|
| Username | Your Pango username or email | — |
| Password | Your Pango password | — |
| Polling interval | How often to check parking status (minutes) | 10 |

The polling interval can be changed later in the integration options.

## Automation Blueprint

Get notified when parking starts, ends, or hourly while active:

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Ferezdaniel7%2Fpango_parking_integration%2Fblob%2Fmaster%2Fblueprints%2Fautomation%2Fpango_parking%2Fparking_notifications.yaml)

> **Note:** HACS does not install blueprints automatically — use the button above to import.

Template variables available in actions: `parking_active`, `parking_start`, `parking_end`.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Authentication fails | Re-open integration settings and re-enter credentials |
| Entities not updating | Press **Poll now** and check Home Assistant logs |
| Sensor shows "Unavailable" | Usually resolves on next poll; check network connectivity |

## Limitations

- **Read-only** — starting/stopping parking is not supported (Pango requires CAPTCHA).
- Single car per account (multi-car support planned — [#5](https://github.com/erezdaniel7/pango_parking_integration/issues/5)).

## Disclaimer

This project is not affiliated with or endorsed by Pango.
