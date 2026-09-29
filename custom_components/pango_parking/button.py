"""Button entities for Pango Parking."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import PangoParkingDataUpdateCoordinator
from .data import PangoConfigEntry
from .entity import PangoBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PangoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pango Parking button from a config entry."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        PangoPollNowButton(coordinator, car_id) for car_id in (coordinator.data or {})
    )


class PangoPollNowButton(PangoBaseEntity, ButtonEntity):
    """Button that triggers an immediate data poll."""

    _unique_id_suffix = "poll_now"
    _attr_translation_key = "poll_now"
    _attr_icon = "mdi:refresh"

    def __init__(
        self, coordinator: PangoParkingDataUpdateCoordinator, car_id: str
    ) -> None:
        super().__init__(coordinator, car_id)

    async def async_press(self) -> None:
        """Trigger an immediate coordinator refresh and wait for completion."""
        await self.coordinator.async_refresh()
