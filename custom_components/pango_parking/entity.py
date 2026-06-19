"""Base entity class for Pango Parking."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PangoParkingDataUpdateCoordinator


class PangoBaseEntity(CoordinatorEntity[PangoParkingDataUpdateCoordinator]):
    """Base entity for all Pango Parking entities."""

    _attr_has_entity_name = True
    _unique_id_suffix: str

    @property
    def unique_id(self) -> str:
        """Return unique ID incorporating the car ID when available."""
        car_id = self.coordinator.data.get("car_id") if self.coordinator.data else None
        entry_id = self.coordinator.config_entry.entry_id
        prefix = f"{entry_id}_{car_id}" if car_id else entry_id
        return f"{prefix}_{self._unique_id_suffix}"

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info grouped by car ID."""
        car_id = self.coordinator.data.get("car_id") if self.coordinator.data else None
        if not car_id:
            return None
        return DeviceInfo(
            identifiers={(DOMAIN, car_id)},
            name=f"Car {car_id}",
            manufacturer="Pango",
        )
