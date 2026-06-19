"""Config flow for Pango Parking integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

from .api import PangoApiClient, PangoApiError, PangoAuthError
from .const import (
    CONF_POLL_INTERVAL_MINUTES,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
    MAX_POLL_INTERVAL_MINUTES,
    MIN_POLL_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate user input by attempting login and one status fetch."""
    client = PangoApiClient(
        async_get_clientsession(hass),
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )
    await client.async_fetch_parking_status()


def _build_user_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config flow schema."""
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=user_input.get(CONF_USERNAME, "")): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
            vol.Optional(
                CONF_POLL_INTERVAL_MINUTES,
                default=user_input.get(CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_POLL_INTERVAL_MINUTES,
                    max=MAX_POLL_INTERVAL_MINUTES,
                    step=1,
                    mode="box",
                )
            ),
        }
    )


def _build_options_schema(options: dict[str, Any]) -> vol.Schema:
    """Build options flow schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_POLL_INTERVAL_MINUTES,
                default=options.get(CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_POLL_INTERVAL_MINUTES,
                    max=MAX_POLL_INTERVAL_MINUTES,
                    step=1,
                    mode="box",
                )
            ),
        }
    )


class PangoParkingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pango Parking."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip().lower()
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()

            try:
                await _validate_input(self.hass, user_input)
            except PangoAuthError:
                errors["base"] = "invalid_auth"
            except PangoApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during Pango setup")
                errors["base"] = "unknown"
            else:
                data = {
                    CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                options = {
                    CONF_POLL_INTERVAL_MINUTES: int(
                        user_input.get(CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES)
                    )
                }
                return self.async_create_entry(
                    title=f"Pango ({data[CONF_USERNAME]})",
                    data=data,
                    options=options,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> PangoParkingOptionsFlow:
        """Get the options flow for this handler."""
        return PangoParkingOptionsFlow()


class PangoParkingOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Pango Parking."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_POLL_INTERVAL_MINUTES: int(user_input[CONF_POLL_INTERVAL_MINUTES])},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema(self.config_entry.options),
        )
