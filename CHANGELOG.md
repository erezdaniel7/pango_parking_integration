# Changelog

All notable changes to the Pango Parking integration will be documented in this file.

## [0.4.4] - 2026-07-17

### Fixed
- **Sensor going Unavailable on timeout**: When the Pango API times out, the integration now returns the last known good data instead of marking all sensors as Unavailable. This prevents the "Is parking active" sensor from flickering to Unavailable during transient network issues.

## [0.4.3] - 2026-06-27

### Fixed
- **hassfest**: `manifest.json` keys now sorted correctly (`domain`, `name`, then alphabetical)
- **HACS validation**: Removed invalid `domains` key from `hacs.json`
- **HACS validation**: Added GitHub repo description and topics (`home-assistant`, `hacs`, `hacs-integration`, `custom-component`, `parking`, `pango`)


### Fixed
- **Duplicate entity**: `sensor.is_parking_active` from v0.3.0 was left as a stale orphan after migration to `binary_sensor`. Added automatic cleanup in `async_setup_entry` to remove it on next HA restart.


### Fixed
- **HACS install error**: Removed `zip_release: true` from `hacs.json` — HACS was looking for a `.zip` asset in the release and failing with `NoneType` error because no zip was provided
- **Logo not appearing in HA**: Re-saved `brand/icon.png` as proper RGBA PNG (was incorrectly saved as palette mode P after quantization)


### Fixed
- **HACS ecosystem compliance**: 7 blocking issues that caused hassfest/HACS validation to fail
- **Logo now visible in HA**: Moved icon to `brand/` subdirectory (HA 2026.3+ requirement); compressed from 143 KB → 4.2 KB (256×256); added `icon@2x.png` (512×512) for Retina displays
- **Auth re-prompt**: Coordinator now raises `ConfigEntryAuthFailed` on persistent login failure, triggering HA's built-in re-authentication UI instead of silently failing
- **Entity availability**: Sensors no longer show as "available" when the coordinator is in an error state
- **`is_parking_active` entity type**: Moved from `SensorEntity` to `BinarySensorEntity` (correct type for on/off state)
- **Blueprint**: Updated trigger to use `to: "on"` / `from: "on"` (proper binary sensor states); updated sensor selector to `domain: binary_sensor`
- **Blueprint import**: Added one-click import badge to README

### Added
- **GitHub Actions CI**: `validate.yml` (hassfest + HACS validation, runs daily), `lint.yml` (Ruff), `release.yml` (auto GitHub Release on tag push)
- **`binary_sensor.py`**: New platform for the parking active binary sensor
- **`entity.py`**: Base entity class (`PangoBaseEntity`) eliminating code duplication
- **`data.py`**: Typed `PangoConfigEntry` alias and `PangoRuntimeData` dataclass

### Changed
- Migrated from deprecated `hass.data[DOMAIN]` to `entry.runtime_data` pattern
- `manifest.json`: Added `codeowners`, `documentation`, `issue_tracker`
- `hacs.json`: Added `zip_release: true`, `hide_default_branch: true`, `homeassistant: 2024.6.0`
- `config_flow.py`: Removed deprecated `OptionsFlow.__init__`; exceptions now logged; added return type annotations
- `const.py`: Removed `SensorDeviceClass` import and `DATA_COORDINATOR` constant


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
