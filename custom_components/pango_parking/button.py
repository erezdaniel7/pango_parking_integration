"""Button entities for Pango Parking."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
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
        self._entry = entry

    @property
    def unique_id(self) -> str:
        """Return unique ID with car_id."""
        car_id = self.coordinator.data.get("car_id") if self.coordinator.data else None
        if car_id:
            return f"{self._entry.entry_id}_{car_id}_poll_now"
        return f"{self._entry.entry_id}_poll_now"

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        car_id = self.coordinator.data.get("car_id") if self.coordinator.data else None
        if not car_id:
            return None

        return DeviceInfo(
            identifiers={(DOMAIN, car_id)},
            name=f"Car {car_id}",
            manufacturer="Pango",
        )

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
