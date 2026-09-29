"""Base entity class for Pango Parking."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PangoParkingDataUpdateCoordinator


class PangoBaseEntity(CoordinatorEntity[PangoParkingDataUpdateCoordinator]):
    """Base entity for all Pango Parking entities."""

    _attr_has_entity_name = True
    _unique_id_suffix: str

    def __init__(
        self, coordinator: PangoParkingDataUpdateCoordinator, car_id: str
    ) -> None:
        super().__init__(coordinator)
        self._car_id = car_id

    @property
    def car_data(self) -> dict[str, Any] | None:
        """Return coordinator data for this entity's car."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._car_id)

    @property
    def unique_id(self) -> str:
        """Return unique ID incorporating the car ID."""
        entry_id = self.coordinator.config_entry.entry_id
        return f"{entry_id}_{self._car_id}_{self._unique_id_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info grouped by car ID."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._car_id)},
            name=f"Car {self._car_id}",
            manufacturer="Pango",
        )
