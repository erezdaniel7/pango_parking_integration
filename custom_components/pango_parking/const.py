"""Constants for the Pango Parking integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import Platform

DOMAIN = "pango_parking"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

CONF_POLL_INTERVAL_MINUTES = "poll_interval_minutes"
DEFAULT_POLL_INTERVAL_MINUTES = 10
MIN_POLL_INTERVAL_MINUTES = 1
MAX_POLL_INTERVAL_MINUTES = 120

DATA_COORDINATOR = "coordinator"

LOGIN_URL = "https://admin.pango.co.il/Driver/logindriver.aspx"
PARKING_URL = "https://admin.pango.co.il/Driver/ParkACar.aspx"

TIMEZONE = "Asia/Jerusalem"

SENSOR_KEY_ACTIVE = "is_parking_active"
SENSOR_KEY_START = "parking_start_time"
SENSOR_KEY_END = "parking_end_time"

SENSOR_DEVICE_CLASSES: dict[str, SensorDeviceClass | None] = {
    SENSOR_KEY_ACTIVE: None,
    SENSOR_KEY_START: SensorDeviceClass.TIMESTAMP,
    SENSOR_KEY_END: SensorDeviceClass.TIMESTAMP,
}
