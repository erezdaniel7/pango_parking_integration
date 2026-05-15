"""API client for Pango Parking."""

from __future__ import annotations

import html
import logging
import re
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import LOGIN_URL, PARKING_URL, TIMEZONE
from .parser import parse_parking_page

_LOGGER = logging.getLogger(__name__)

LOGIN_PAGE_MARKERS = ("txtUserName", "txtPassword", "btnLogin")


class PangoApiError(Exception):
    """Base exception for Pango API issues."""


class PangoAuthError(PangoApiError):
    """Authentication failed or session expired."""


class PangoApiClient:
    """Pango web client using authenticated session cookies."""

    def __init__(self, session: ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._timeout = ClientTimeout(total=20)
        self._authenticated = False

    async def async_fetch_parking_status(self) -> dict[str, Any]:
        """Fetch and parse parking status."""
        if not self._authenticated:
            await self.async_login()

        page_html = await self._request_text("GET", PARKING_URL)
        if self._is_login_page(page_html):
            self._authenticated = False
            raise PangoAuthError("Session expired")

        return parse_parking_page(page_html, TIMEZONE)

    async def async_login(self) -> None:
        """Authenticate against Pango login form."""
        login_html = await self._request_text("GET", LOGIN_URL)
        hidden_fields = _extract_hidden_form_fields(login_html)

        payload = dict(hidden_fields)
        payload.update(
            {
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "TextBox1": "",
                "txtUserName": self._username,
                "txtPassword": self._password,
                "btnLogin": "כניסה >",
            }
        )

        response_html = await self._request_text("POST", LOGIN_URL, data=payload)

        # Validate by opening parking page with same session.
        parking_html = await self._request_text("GET", PARKING_URL)
        if self._is_login_page(response_html) and self._is_login_page(parking_html):
            self._authenticated = False
            raise PangoAuthError("Invalid username/password")

        self._authenticated = True

    async def _request_text(
        self,
        method: str,
        url: str,
        data: dict[str, str] | None = None,
    ) -> str:
        try:
            async with self._session.request(
                method,
                url,
                data=data,
                timeout=self._timeout,
                allow_redirects=True,
            ) as response:
                text = await response.text()
                if response.status >= 400:
                    raise PangoApiError(f"HTTP {response.status} from {url}")
                return text
        except ClientError as err:
            raise PangoApiError("Connection error while calling Pango") from err

    @staticmethod
    def _is_login_page(page_html: str) -> bool:
        lowered = page_html.lower()
        return all(marker.lower() in lowered for marker in LOGIN_PAGE_MARKERS)


def _extract_hidden_form_fields(page_html: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    hidden_input_re = re.compile(
        r'<input[^>]*type="hidden"[^>]*>',
        re.IGNORECASE,
    )

    for tag in hidden_input_re.findall(page_html):
        name_match = re.search(r'name="([^"]+)"', tag, re.IGNORECASE)
        if not name_match:
            continue

        name = name_match.group(1)
        value_match = re.search(r'value="([^"]*)"', tag, re.IGNORECASE)
        value = value_match.group(1) if value_match else ""
        fields[name] = html.unescape(value)

    # Fallback to direct extraction for known critical fields in case input order/shape differs.
    for critical in (
        "__VIEWSTATE",
        "__EVENTVALIDATION",
        "__VIEWSTATEGENERATOR",
        "__VIEWSTATEENCRYPTED",
    ):
        if critical not in fields:
            direct = _extract_hidden_value(page_html, critical)
            if direct is not None:
                fields[critical] = direct

    return fields


def _extract_hidden_value(page_html: str, name: str) -> str | None:
    pattern = (
        rf'<input[^>]*name="{re.escape(name)}"[^>]*value="([^"]*)"[^>]*>'
        rf'|<input[^>]*value="([^"]*)"[^>]*name="{re.escape(name)}"[^>]*>'
    )
    match = re.search(pattern, page_html, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1) if match.group(1) is not None else match.group(2)
    return html.unescape(value)
