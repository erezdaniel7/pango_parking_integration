"""Pango Parking integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, PLATFORMS, SENSOR_KEY_ACTIVE
from .coordinator import PangoParkingDataUpdateCoordinator
from .data import PangoConfigEntry, PangoRuntimeData


def _remove_stale_sensor_entities(hass: HomeAssistant, entry: PangoConfigEntry) -> None:
    """Remove is_parking_active from the sensor platform (moved to binary_sensor in 0.4.0)."""
    registry = er.async_get(hass)
    stale = [
        entity
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.domain == "sensor"
        and entity.unique_id.endswith(f"_{SENSOR_KEY_ACTIVE}")
    ]
    for entity in stale:
        registry.async_remove(entity.entity_id)


async def async_setup_entry(hass: HomeAssistant, entry: PangoConfigEntry) -> bool:
    """Set up Pango Parking from a config entry."""
    _remove_stale_sensor_entities(hass, entry)

    coordinator = PangoParkingDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = PangoRuntimeData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PangoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: PangoConfigEntry) -> None:
    """Handle options update by reloading the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

