"""HTML parsing helpers for Pango Parking pages."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
import html
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ACTIVE_TABLE_ID = 'id="ctl00_ContentPlaceHolder1_tblExist"'
INACTIVE_ROW_ID = 'id="ctl00_ContentPlaceHolder1_trNewParkingTitle"'
STOP_BUTTON_ID = 'id="ctl00_ContentPlaceHolder1_btnStop"'
START_BUTTON_ID = 'id="ctl00_ContentPlaceHolder1_btnStartParking"'

TARGET_DATE_RE = re.compile(r"TargetDate\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
SPAN_BY_ID_RE_TEMPLATE = r'<span[^>]+id="{element_id}"[^>]*>(.*?)</span>'
LABEL_ROW_RE_TEMPLATE = (
    r"<td[^>]*>\s*{label}\s*</td>\s*<td[^>]*>(.*?)</td>"
)
TIME_RE = re.compile(r"^\d{2}:\d{2}:\d{2}$")


def parse_parking_page(page_html: str, timezone_name: str) -> dict[str, Any]:
    """Parse parking status from Pango ParkACar page HTML."""
    is_active = ACTIVE_TABLE_ID in page_html or STOP_BUTTON_ID in page_html
    is_inactive = INACTIVE_ROW_ID in page_html or START_BUTTON_ID in page_html

    start_raw = _extract_start_time(page_html)
    end_raw = _extract_end_time(page_html)
    target_raw = _extract_target_date(page_html)

    tz = _resolve_timezone(timezone_name)
    target_dt = _parse_target_datetime(target_raw, tz)
    start_dt = _parse_time_with_reference_date(start_raw, target_dt, tz)
    end_dt = _parse_time_with_reference_date(end_raw, target_dt, tz)

    if target_dt is not None and end_dt is None:
        end_dt = target_dt

    return {
        "is_active": is_active,
        "is_inactive": is_inactive,
        "start_time": start_dt,
        "end_time": end_dt,
        "start_time_raw": start_raw,
        "end_time_raw": end_raw,
        "target_date_raw": target_raw,
    }


def _extract_target_date(page_html: str) -> str | None:
    match = TARGET_DATE_RE.search(page_html)
    if not match:
        return None
    return html.unescape(match.group(1).strip())


def _extract_span_by_id(page_html: str, element_id: str) -> str | None:
    pattern = SPAN_BY_ID_RE_TEMPLATE.format(element_id=re.escape(element_id))
    match = re.search(pattern, page_html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    raw = re.sub(r"<[^>]+>", "", match.group(1))
    text = html.unescape(raw).strip()
    return text or None


def _extract_time_from_label_row(page_html: str, label: str) -> str | None:
    escaped_label = re.escape(label)
    pattern = LABEL_ROW_RE_TEMPLATE.format(label=escaped_label)
    match = re.search(pattern, page_html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    raw = re.sub(r"<[^>]+>", "", match.group(1))
    text = html.unescape(raw).strip()
    if TIME_RE.match(text):
        return text
    return None


def _extract_start_time(page_html: str) -> str | None:
    by_id = _extract_span_by_id(page_html, "ctl00_ContentPlaceHolder1_lblFrom")
    if by_id and TIME_RE.match(by_id):
        return by_id

    for label in ("זמן התחלה:", "זמן התחלה"):
        by_label = _extract_time_from_label_row(page_html, label)
        if by_label:
            return by_label
    return None


def _extract_end_time(page_html: str) -> str | None:
    by_id = _extract_span_by_id(page_html, "ctl00_ContentPlaceHolder1_lblTo")
    if by_id and TIME_RE.match(by_id):
        return by_id

    for label in ("זמן סיום:", "זמן סיום"):
        by_label = _extract_time_from_label_row(page_html, label)
        if by_label:
            return by_label
    return None


def _parse_target_datetime(value: str | None, tz: tzinfo) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        return None
    return parsed.replace(tzinfo=tz)


def _parse_time_with_reference_date(
    value: str | None,
    reference: datetime | None,
    tz: tzinfo,
) -> datetime | None:
    if not value or not TIME_RE.match(value):
        return None

    try:
        clock = datetime.strptime(value, "%H:%M:%S").time()
    except ValueError:
        return None

    date_source = reference.astimezone(tz).date() if reference else datetime.now(tz).date()
    combined = datetime.combine(date_source, clock, tzinfo=tz)

    # Parking may span midnight, so if start appears after end reference, shift to previous day.
    if reference and combined > reference:
        combined = combined - timedelta(days=1)

    return combined


def _resolve_timezone(timezone_name: str) -> tzinfo:
    """Resolve timezone and gracefully fallback if tzdata is unavailable."""
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return timezone.utc
