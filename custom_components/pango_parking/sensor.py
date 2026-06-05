"""Sensor entities for Pango Parking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    SENSOR_DEVICE_CLASSES,
    SENSOR_KEY_ACTIVE,
    SENSOR_KEY_END,
    SENSOR_KEY_START,
)
from .coordinator import PangoParkingDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class PangoSensorEntityDescription(SensorEntityDescription):
    """Pango sensor entity description."""

    value_fn: Callable[[dict], bool | datetime | None]


SENSOR_DESCRIPTIONS: tuple[PangoSensorEntityDescription, ...] = (
    PangoSensorEntityDescription(
        key=SENSOR_KEY_ACTIVE,
        translation_key=SENSOR_KEY_ACTIVE,
        icon="mdi:car",
        value_fn=lambda data: data.get("is_active"),
        device_class=SENSOR_DEVICE_CLASSES[SENSOR_KEY_ACTIVE],
    ),
    PangoSensorEntityDescription(
        key=SENSOR_KEY_START,
        translation_key=SENSOR_KEY_START,
        icon="mdi:clock-start",
        value_fn=lambda data: data.get("start_time"),
        device_class=SENSOR_DEVICE_CLASSES[SENSOR_KEY_START],
    ),
    PangoSensorEntityDescription(
        key=SENSOR_KEY_END,
        translation_key=SENSOR_KEY_END,
        icon="mdi:clock-end",
        value_fn=lambda data: data.get("end_time"),
        device_class=SENSOR_DEVICE_CLASSES[SENSOR_KEY_END],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PangoParkingDataUpdateCoordinator = data[DATA_COORDINATOR]

    entities = [
        PangoParkingSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class PangoParkingSensor(CoordinatorEntity[PangoParkingDataUpdateCoordinator], SensorEntity):
    """Representation of a Pango Parking sensor."""

    entity_description: PangoSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PangoParkingDataUpdateCoordinator,
        entry: ConfigEntry,
        description: PangoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry

    @property
    def unique_id(self) -> str:
        """Return unique ID with car_id."""
        car_id = self.coordinator.data.get("car_id") if self.coordinator.data else None
        if car_id:
            return f"{self._entry.entry_id}_{car_id}_{self.entity_description.key}"
        return f"{self._entry.entry_id}_{self.entity_description.key}"

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

    @property
    def available(self) -> bool:
        """Stay available on errors as long as we have previously fetched data."""
        return self.coordinator.data is not None

    @property
    def native_value(self) -> bool | datetime | None:
        data = self.coordinator.data or {}
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        data = self.coordinator.data or {}
        if self.entity_description.key == SENSOR_KEY_START:
            return {"raw_time": data.get("start_time_raw")}
        if self.entity_description.key == SENSOR_KEY_END:
            return {
                "raw_time": data.get("end_time_raw"),
                "target_date_raw": data.get("target_date_raw"),
            }
        return {}
