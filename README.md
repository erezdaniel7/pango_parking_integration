# Pango Parking

Home Assistant custom integration for reading active parking status from Pango.

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue.svg)](https://www.home-assistant.io/)

## Overview

This integration logs in to Pango, reads parking status from the driver portal, and exposes entities in Home Assistant.

### Features

- UI config flow (username + password)
- Configurable polling interval in minutes (default 10)
- Poll now button for manual refresh
- Automatic re-login when the session expires

### Entities

- Sensor: Is parking active
- Sensor: Parking start time
- Sensor: Parking end time
- Button: Poll now

## Installation

### Option 1: HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=erezdaniel7&repository=pango_parking_integration&category=Integration)

1. Open HACS.
2. Go to Integrations.
3. Open the menu and select Custom repositories.
4. Add https://github.com/erezdaniel7/pango_parking_integration.
5. Set category to Integration.
6. Install Pango Parking from HACS.
7. Restart Home Assistant.

### Option 2: Manual

1. Copy folder custom_components/pango_parking to your Home Assistant config custom_components directory.
2. Restart Home Assistant.

## Setup

1. In Home Assistant, open Settings -> Devices and Services.
2. Click Add Integration.
3. Search for Pango Parking.
4. Enter:
   - Username
   - Password
   - Polling interval (minutes)

## Configuration Details

- Username: Pango username/email
- Password: Pango password
- Polling interval: default 10 minutes, configurable in integration options

## Notes

- Read-only integration in current version.
- Start/stop parking actions are not implemented.
- Data is parsed from Pango ParkACar.aspx page response.

### Current behavior

- Active parking: exposes active state plus start/end parking times.
- Inactive parking: exposes inactive state with no start/end values.
- Pango start/stop actions may require CAPTCHA in the website flow. This integration does not perform those actions.

## Troubleshooting

- If authentication fails, re-open integration settings and re-enter credentials.
- If entities do not update, press Poll now and check Home Assistant logs.
- If parsing breaks after a Pango site change, refresh a new HAR capture and update selectors.

## Disclaimer

This project is not affiliated with or endorsed by Pango.
