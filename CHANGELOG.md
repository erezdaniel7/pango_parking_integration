# Changelog

All notable changes to the Pango Parking integration will be documented in this file.

## [0.3.0] - 2026-06-15

### Added
- **Automation Blueprint**: New blueprint for parking notifications with three trigger types:
  - Notification when parking starts
  - Notification when parking ends
  - Hourly reminder while parking is still active
  - Blueprint supports custom actions for any notification service (mobile app, Telegram, etc.)
  - Template variables available: `parking_active`, `parking_start`, `parking_end`
  - Blueprint URL: `https://raw.githubusercontent.com/erezdaniel7/pango_parking_integration/main/blueprints/automation/pango_parking/parking_notifications.yaml`

- **Integration Logo**: Added custom parking icon badge for Home Assistant UI display

- **Release Management**: Configured HACS to track GitHub releases instead of commit hashes
  - Added `zip_release: true` to hacs.json
  - Added `hide_default_branch: true` to hacs.json
  - Home Assistant will now show semantic version numbers (e.g., 0.3.0) instead of commit IDs

### Changed
- Updated manifest version to 0.3.0
- Enhanced README with blueprint documentation and setup instructions

### Documentation
- Added section on how to use the parking notifications blueprint
- Added instructions for GitHub releases to display proper version numbers in HA

## [0.2.1] - Previous release

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
