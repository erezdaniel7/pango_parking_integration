"""Diagnostics support for Pango Parking."""

from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.diagnostics import async_redact_data

from .data import PangoConfigEntry

TO_REDACT = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "__VIEWSTATE",
    "__EVENTVALIDATION",
    "__VIEWSTATEGENERATOR",
    "__VIEWSTATEENCRYPTED",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: PangoConfigEntry,
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    diagnostics = {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception)
            if coordinator.last_exception
            else None,
            "data": coordinator.data,
        },
    }

    return async_redact_data(diagnostics, TO_REDACT)

