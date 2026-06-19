"""Binary sensor entities for Pango Parking."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SENSOR_KEY_ACTIVE
from .coordinator import PangoParkingDataUpdateCoordinator
from .data import PangoConfigEntry
from .entity import PangoBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PangoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pango Parking binary sensor from a config entry."""
    async_add_entities([PangoParkingActiveSensor(entry.runtime_data.coordinator)])


class PangoParkingActiveSensor(PangoBaseEntity, BinarySensorEntity):
    """Binary sensor indicating whether parking is currently active."""

    _unique_id_suffix = SENSOR_KEY_ACTIVE
    _attr_translation_key = SENSOR_KEY_ACTIVE
    _attr_icon = "mdi:car"

    def __init__(self, coordinator: PangoParkingDataUpdateCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def is_on(self) -> bool | None:
        """Return True when parking is active."""
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.get("is_active"))
