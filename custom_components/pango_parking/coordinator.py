"""Data update coordinator for Pango Parking."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PangoApiClient, PangoApiError, PangoAuthError
from .const import CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PangoParkingDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Pango Parking data updates."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._session: ClientSession = async_get_clientsession(hass)
        self._client = PangoApiClient(
            self._session,
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )

        update_interval = timedelta(
            minutes=entry.options.get(
                CONF_POLL_INTERVAL_MINUTES,
                DEFAULT_POLL_INTERVAL_MINUTES,
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self._client.async_fetch_parking_status()
        except PangoAuthError as err:
            _LOGGER.debug("Pango auth failed, trying one re-login: %s", err)
            try:
                await self._client.async_login()
                return await self._client.async_fetch_parking_status()
            except PangoAuthError as second_err:
                raise ConfigEntryAuthFailed(
                    f"Invalid credentials: {second_err}"
                ) from second_err
            except PangoApiError as second_err:
                raise UpdateFailed(f"API error after re-login: {second_err}") from second_err
        except PangoApiError as err:
            raise UpdateFailed(str(err)) from err

