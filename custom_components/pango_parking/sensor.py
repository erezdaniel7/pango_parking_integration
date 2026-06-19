"""Sensor entities for Pango Parking."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SENSOR_KEY_END, SENSOR_KEY_START
from .coordinator import PangoParkingDataUpdateCoordinator
from .data import PangoConfigEntry
from .entity import PangoBaseEntity


@dataclass(frozen=True, kw_only=True)
class PangoSensorEntityDescription(SensorEntityDescription):
    """Pango sensor entity description."""

    value_fn: Callable[[dict], datetime | None]


SENSOR_DESCRIPTIONS: tuple[PangoSensorEntityDescription, ...] = (
    PangoSensorEntityDescription(
        key=SENSOR_KEY_START,
        translation_key=SENSOR_KEY_START,
        icon="mdi:clock-start",
        value_fn=lambda data: data.get("start_time"),
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    PangoSensorEntityDescription(
        key=SENSOR_KEY_END,
        translation_key=SENSOR_KEY_END,
        icon="mdi:clock-end",
        value_fn=lambda data: data.get("end_time"),
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PangoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pango Parking sensors from a config entry."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        PangoParkingSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class PangoParkingSensor(PangoBaseEntity, SensorEntity):
    """Representation of a Pango Parking sensor."""

    entity_description: PangoSensorEntityDescription

    def __init__(
        self,
        coordinator: PangoParkingDataUpdateCoordinator,
        description: PangoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._unique_id_suffix = description.key

    @property
    def available(self) -> bool:
        """Return availability — requires both coordinator success and data present."""
        return super().available and self.coordinator.data is not None

    @property
    def native_value(self) -> datetime | None:
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

