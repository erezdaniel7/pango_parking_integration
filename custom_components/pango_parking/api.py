"""API client for Pango Parking."""

from __future__ import annotations

import html
import logging
import re
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import LOGIN_URL, PARKING_URL, TIMEZONE
from .parser import CarOption, parse_car_options, parse_parking_page

_LOGGER = logging.getLogger(__name__)

LOGIN_PAGE_MARKERS = ("txtUserName", "txtPassword", "btnLogin")
CAR_SELECTOR_FIELD = "ctl00$ContentPlaceHolder1$cboCars"
SELECT_RE = re.compile(
    r"<select(?P<attributes>[^>]*)>(?P<options>.*?)</select>",
    re.IGNORECASE | re.DOTALL,
)
OPTION_RE = re.compile(
    r"<option(?P<attributes>[^>]*)>(?P<label>.*?)</option>",
    re.IGNORECASE | re.DOTALL,
)


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
        """Fetch the currently selected car status for compatibility."""
        page_html = await self._async_fetch_parking_page()
        return parse_parking_page(page_html, TIMEZONE)

    async def async_fetch_parking_statuses(self) -> dict[str, dict[str, Any]]:
        """Fetch and parse parking status for every car on the account."""
        page_html = await self._async_fetch_parking_page()

        cars = parse_car_options(page_html)
        if not cars:
            raise PangoApiError("No cars found on Pango parking page")

        if len({car.car_id for car in cars}) != len(cars):
            raise PangoApiError("Duplicate cars found on Pango parking page")

        statuses: dict[str, dict[str, Any]] = {}
        selected = next((car for car in cars if car.selected), None)
        if selected is None:
            raise PangoApiError("Pango parking page has no selected car")

        statuses[selected.car_id] = parse_parking_page(page_html, TIMEZONE)
        current_html = page_html

        for car in cars:
            if car == selected:
                continue
            current_html = await self._select_car(current_html, car)
            statuses[car.car_id] = parse_parking_page(current_html, TIMEZONE)

        return {car.car_id: statuses[car.car_id] for car in cars}

    async def _async_fetch_parking_page(self) -> str:
        """Fetch the parking page with an authenticated session."""
        if not self._authenticated:
            await self.async_login()

        page_html = await self._request_text("GET", PARKING_URL)
        if self._is_login_page(page_html):
            self._authenticated = False
            raise PangoAuthError("Session expired")
        return page_html

    async def _select_car(self, page_html: str, car: CarOption) -> str:
        """Select a car using the parking page's ASP.NET postback."""
        payload = _extract_postback_form_fields(page_html)
        payload.update(
            {
                "__EVENTTARGET": CAR_SELECTOR_FIELD,
                "__EVENTARGUMENT": "",
                CAR_SELECTOR_FIELD: car.value,
            }
        )
        response_html = await self._request_text("POST", PARKING_URL, data=payload)
        if self._is_login_page(response_html):
            self._authenticated = False
            raise PangoAuthError("Session expired")

        selected = next(
            (option for option in parse_car_options(response_html) if option.selected),
            None,
        )
        if selected is None or selected.car_id != car.car_id:
            raise PangoApiError(f"Pango did not select requested car {car.car_id}")
        return response_html

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
        except TimeoutError as err:
            raise PangoApiError("Timeout fetching pango_parking data") from err

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


def _extract_postback_form_fields(page_html: str) -> dict[str, str]:
    """Extract the fields a browser submits during a full ASP.NET postback."""
    fields = _extract_hidden_form_fields(page_html)

    for select_match in SELECT_RE.finditer(page_html):
        name = _extract_attribute(select_match.group("attributes"), "name")
        if not name:
            continue

        options = list(OPTION_RE.finditer(select_match.group("options")))
        selected = next(
            (
                option
                for option in options
                if re.search(
                    r"\bselected\b",
                    option.group("attributes"),
                    re.IGNORECASE,
                )
            ),
            options[0] if options else None,
        )
        if selected is None:
            continue

        value = _extract_attribute(selected.group("attributes"), "value")
        if value is None:
            value = re.sub(r"<[^>]+>", "", selected.group("label")).strip()
        fields[name] = html.unescape(value)

    return fields


def _extract_attribute(attributes: str, name: str) -> str | None:
    match = re.search(
        rf"""\b{re.escape(name)}\s*=\s*["']([^"']*)["']""",
        attributes,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


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
