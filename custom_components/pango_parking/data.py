"""Typed config entry and runtime data for Pango Parking."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .coordinator import PangoParkingDataUpdateCoordinator


@dataclass
class PangoRuntimeData:
    """Runtime data stored on the config entry."""

    coordinator: PangoParkingDataUpdateCoordinator


type PangoConfigEntry = ConfigEntry[PangoRuntimeData]
