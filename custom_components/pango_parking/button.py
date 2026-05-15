"""Button entities for Pango Parking."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PangoParkingDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PangoParkingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([PangoPollNowButton(coordinator, entry)])


class PangoPollNowButton(CoordinatorEntity[PangoParkingDataUpdateCoordinator], ButtonEntity):
    """Button that triggers immediate poll."""

    _attr_has_entity_name = True
    _attr_translation_key = "poll_now"
    _attr_icon = "mdi:refresh"

    def __init__(
        self,
        coordinator: PangoParkingDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_poll_now"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
