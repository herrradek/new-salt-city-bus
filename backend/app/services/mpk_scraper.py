"""Scrapes and parses MPK Łódź timetable pages, with static data fallback."""

from __future__ import annotations

import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.app.core.mpk_config import CACHE_TTL_SECONDS, MPK_BASE_URL

_cache: dict[str, tuple[float, dict]] = {}

_STATIC_DATA_PATH = Path(__file__).parent.parent / "data" / "timetables.json"
_static_data: dict | None = None


def _load_static_data() -> dict:
    global _static_data
    if _static_data is None:
        with open(_STATIC_DATA_PATH) as f:
            _static_data = json.load(f)
    return _static_data


def _cache_key(line_id: int, timetable_id: int, direction: int, stop_number: int) -> str:
    return f"{line_id}_{timetable_id}_{direction}_{stop_number}"


def _build_url(line_id: int, timetable_id: int, direction: int, stop_number: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return (
        f"{MPK_BASE_URL}/tabliczka.jsp"
        f"?direction={direction}&lineId={line_id}"
        f"&timetableId={timetable_id}&stopNumber={stop_number}"
        f"&date={now}"
    )


def _get_static_timetable(key: str) -> dict[str, list[dict]] | None:
    """Load timetable from static JSON file."""
    data = _load_static_data()
    entry = data.get(key)
    if not entry:
        return None
    result = {}
    for day_type in ("ROBOCZY", "SOBOTY", "NIEDZIELA"):
        pairs = entry.get(day_type, [])
        result[day_type] = [{"hour": h, "minute": m} for h, m in pairs]
    return result


# --- HTML parsing (used when live fetch succeeds) ---

def _parse_timetable_html(html: str) -> dict[str, list[dict]]:
    schedules: dict[str, list[dict]] = {}

    day_type_names = re.findall(r'day_type_name_\d+[^>]*>\s*([^<]+)', html)

    def normalize(name: str) -> str:
        name = name.strip().upper()
        if "ROBOCZ" in name or "POWSZED" in name:
            return "ROBOCZY"
        if "SOBOT" in name:
            return "SOBOTY"
        if "NIEDZIEL" in name or "ŚWIĘT" in name:
            return "NIEDZIELA"
        return name

    sections = re.split(r'<div[^>]*class="[^"]*dayType[^"]*"', html)

    if len(sections) > 1:
        for i, section in enumerate(sections[1:]):
            day_name = normalize(day_type_names[i]) if i < len(day_type_names) else f"DAY_{i}"
            departures = _extract_departures(section)
            if departures:
                schedules[day_name] = departures

    return schedules


def _extract_departures(html: str) -> list[dict]:
    departures = []
    parts = re.split(r'id="hour_(\d+)"', html)
    for i in range(1, len(parts) - 1, 2):
        try:
            hour = int(parts[i])
        except ValueError:
            continue
        content = parts[i + 1] if i + 1 < len(parts) else ""
        minutes = re.findall(r'table_minute[^>]*>\s*(\d{2})', content)
        for m in minutes:
            minute = int(m)
            if minute < 60:
                departures.append({"hour": hour, "minute": minute})
    return departures


# --- Fetching ---

async def _fetch_live(url: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-sL", "--max-time", "15", url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed ({proc.returncode})")
    html = stdout.decode("utf-8", errors="replace")
    if len(html) < 500:
        raise RuntimeError("Response too short")
    return html


async def fetch_timetable(
    line_id: int, timetable_id: int, direction: int, stop_number: int
) -> dict[str, list[dict]]:
    key = _cache_key(line_id, timetable_id, direction, stop_number)

    cached = _cache.get(key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    # Try live scrape first
    try:
        url = _build_url(line_id, timetable_id, direction, stop_number)
        html = await _fetch_live(url)
        schedules = _parse_timetable_html(html)
        if schedules:
            _cache[key] = (time.time(), schedules)
            return schedules
    except Exception:
        pass

    # Fall back to static data
    static = _get_static_timetable(key)
    if static:
        _cache[key] = (time.time(), static)
        return static

    return {}


def _get_day_type() -> str:
    weekday = datetime.now().weekday()
    if weekday < 5:
        return "ROBOCZY"
    elif weekday == 5:
        return "SOBOTY"
    return "NIEDZIELA"


async def get_next_departures(
    line_id: int,
    timetable_id: int,
    direction: int,
    stop_number: int,
    count: int = 5,
) -> list[dict]:
    schedules = await fetch_timetable(line_id, timetable_id, direction, stop_number)
    day_type = _get_day_type()
    departures = schedules.get(day_type, [])

    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute

    upcoming = []
    for dep in departures:
        dep_minutes = dep["hour"] * 60 + dep["minute"]
        if dep_minutes > current_minutes:
            upcoming.append({
                "time": f"{dep['hour']:02d}:{dep['minute']:02d}",
                "minutes_away": dep_minutes - current_minutes,
            })
            if len(upcoming) >= count:
                break

    return upcoming
