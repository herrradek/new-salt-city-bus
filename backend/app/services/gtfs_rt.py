"""GTFS-RT integration for real-time delay data from MPK Łódź."""
from __future__ import annotations

import asyncio
import csv
import io
import os
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from google.transit import gtfs_realtime_pb2

from backend.app.core.mpk_config import COMMUTES

# --- Configuration ---
TRIP_UPDATES_URL = "https://otwarte.miasto.lodz.pl/wp-content/uploads/2025/06/trip_updates.bin"
GTFS_STATIC_URL = "https://otwarte.miasto.lodz.pl/wp-content/uploads/2025/06/GTFS.zip"
GTFS_ZIP_PATH = Path(__file__).parent.parent / "data" / "GTFS.zip"
RT_POLL_INTERVAL = 20  # seconds

# Map MPK website stop numbers to GTFS stop_ids per direction
# direction 0 = outbound (from Fabryczna), direction 1 = inbound (to Fabryczna)
# These were found by cross-referencing stop_times.txt with our configured stops.
MPK_TO_GTFS_STOPS = {
    # Home → Office: Hiacyntowa NŻ (MPK 72), inbound (dir 1)
    ("53A", "home_to_office"): {"gtfs_stop_ids": {"110"}, "direction_id": "1"},
    ("53B", "home_to_office"): {"gtfs_stop_ids": {"110"}, "direction_id": "1"},
    # Office → Home: Rodziny Poznańskich (MPK 2158), outbound (dir 0)
    ("53A", "office_to_home"): {"gtfs_stop_ids": {"2990"}, "direction_id": "0"},
    ("53B", "office_to_home"): {"gtfs_stop_ids": {"2990"}, "direction_id": "0"},
}

# --- GTFS Static Data (loaded once) ---
# Maps: (route_id, trip_id) -> direction_id
_trip_directions: Dict[str, str] = {}
# Maps: (trip_id, stop_id) -> scheduled arrival time string
_trip_stop_times: Dict[Tuple[str, str], str] = {}
# Set of trip_ids for routes 53A, 53B
_relevant_trip_ids: Set[str] = set()
_static_loaded = False

# --- RT cache ---
# Maps: (route_id, commute_id) -> list of {trip_id, delay_seconds, stop_id}
_rt_delays: Dict[Tuple[str, str], List[dict]] = {}
_rt_timestamp: float = 0


async def _download(url: str) -> bytes:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-sL", "--max-time", "30", url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed ({proc.returncode})")
    return stdout


def _load_static_gtfs():
    """Load route/trip/stop mappings from static GTFS ZIP."""
    global _static_loaded, _trip_directions, _relevant_trip_ids, _trip_stop_times

    if _static_loaded:
        return

    if not GTFS_ZIP_PATH.exists():
        return

    zf = zipfile.ZipFile(GTFS_ZIP_PATH)

    def read_csv_file(name):
        with zf.open(name) as f:
            text = f.read().decode("utf-8-sig")
            return list(csv.DictReader(io.StringIO(text)))

    # Load trips for 53A/53B
    for row in read_csv_file("trips.txt"):
        if row["route_id"] in ("53A", "53B"):
            _trip_directions[row["trip_id"]] = row["direction_id"]
            _relevant_trip_ids.add(row["trip_id"])

    # Load stop_times for relevant trips at our stops
    all_gtfs_stop_ids = set()
    for cfg in MPK_TO_GTFS_STOPS.values():
        all_gtfs_stop_ids.update(cfg["gtfs_stop_ids"])

    for row in read_csv_file("stop_times.txt"):
        if row["trip_id"] in _relevant_trip_ids and row["stop_id"] in all_gtfs_stop_ids:
            _trip_stop_times[(row["trip_id"], row["stop_id"])] = row["arrival_time"]

    _static_loaded = True


async def ensure_static_gtfs():
    """Download GTFS.zip if not present, then load it."""
    if not GTFS_ZIP_PATH.exists():
        try:
            data = await _download(GTFS_STATIC_URL)
            GTFS_ZIP_PATH.write_bytes(data)
        except Exception:
            return
    _load_static_gtfs()


async def fetch_rt_delays():
    """Fetch trip_updates.bin and extract delays for 53A/53B at our stops."""
    global _rt_delays, _rt_timestamp

    if time.time() - _rt_timestamp < RT_POLL_INTERVAL:
        return _rt_delays

    await ensure_static_gtfs()
    if not _static_loaded:
        return _rt_delays

    try:
        data = await _download(TRIP_UPDATES_URL)
    except Exception:
        return _rt_delays

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)

    new_delays: Dict[Tuple[str, str], List[dict]] = {}

    for entity in feed.entity:
        tu = entity.trip_update
        route_id = tu.trip.route_id
        trip_id = tu.trip.trip_id

        if route_id not in ("53A", "53B"):
            continue
        if trip_id not in _relevant_trip_ids:
            continue

        direction_id = _trip_directions.get(trip_id, "")

        # Check each stop time update
        for stu in tu.stop_time_update:
            stop_id = str(stu.stop_id)

            # Find which commute this applies to
            for (r, commute_id), cfg in MPK_TO_GTFS_STOPS.items():
                if r != route_id:
                    continue
                if direction_id != cfg["direction_id"]:
                    continue
                if stop_id not in cfg["gtfs_stop_ids"]:
                    # Also accept delay from nearby stops on the same trip
                    # (the feed often reports delay at current position, not at our stop)
                    pass

                # Get delay - prefer arrival, fall back to departure
                delay = 0
                if stu.HasField('arrival'):
                    delay = stu.arrival.delay
                elif stu.HasField('departure'):
                    delay = stu.departure.delay

                key = (route_id, commute_id)
                if key not in new_delays:
                    new_delays[key] = []
                new_delays[key].append({
                    "trip_id": trip_id,
                    "delay_seconds": delay,
                    "stop_id": stop_id,
                })

    # Also match by direction even if stop doesn't match exactly
    # (feed reports delay at current stop, which may not be our stop yet)
    for entity in feed.entity:
        tu = entity.trip_update
        route_id = tu.trip.route_id
        trip_id = tu.trip.trip_id

        if route_id not in ("53A", "53B"):
            continue
        if trip_id not in _relevant_trip_ids:
            continue

        direction_id = _trip_directions.get(trip_id, "")

        # Get the latest delay from this trip (last stop update)
        latest_delay = None
        for stu in tu.stop_time_update:
            if stu.HasField('arrival'):
                latest_delay = stu.arrival.delay
            elif stu.HasField('departure'):
                latest_delay = stu.departure.delay

        if latest_delay is None:
            continue

        for (r, commute_id), cfg in MPK_TO_GTFS_STOPS.items():
            if r != route_id or direction_id != cfg["direction_id"]:
                continue
            key = (route_id, commute_id)
            # Only add if we don't already have an exact stop match
            if key not in new_delays:
                new_delays[key] = []
            # Avoid duplicates
            existing_trips = {d["trip_id"] for d in new_delays[key]}
            if trip_id not in existing_trips:
                new_delays[key].append({
                    "trip_id": trip_id,
                    "delay_seconds": latest_delay,
                    "stop_id": "estimated",
                })

    _rt_delays = new_delays
    _rt_timestamp = time.time()
    return _rt_delays


def get_delay_for_departure(
    route_id: str,
    commute_id: str,
    scheduled_time: str,
) -> Optional[int]:
    """
    Get delay in seconds for a specific departure.
    Returns None if no RT data available, otherwise delay in seconds
    (positive = late, negative = early).

    Only returns a delay if the trip can be matched to this scheduled_time
    (HH:MM) via static GTFS stop_times.
    """
    key = (route_id, commute_id)
    delays = _rt_delays.get(key, [])
    if not delays:
        return None

    cfg = MPK_TO_GTFS_STOPS.get(key)
    if not cfg:
        return None

    hhmm = scheduled_time[:5]  # "16:09" -> "16:09"

    # Try exact match: trip's scheduled arrival at our stop matches this departure time
    for d in delays:
        trip_id = d["trip_id"]
        for gtfs_stop_id in cfg["gtfs_stop_ids"]:
            sched = _trip_stop_times.get((trip_id, gtfs_stop_id))
            if sched and sched[:5] == hhmm:
                return d["delay_seconds"]

    # Close match: within 3 minutes (MPK timetables round differently than GTFS)
    sched_mins = int(hhmm[:2]) * 60 + int(hhmm[3:5])
    for d in delays:
        trip_id = d["trip_id"]
        for gtfs_stop_id in cfg["gtfs_stop_ids"]:
            sched = _trip_stop_times.get((trip_id, gtfs_stop_id))
            if sched:
                try:
                    trip_mins = int(sched[:2]) * 60 + int(sched[3:5])
                    if abs(trip_mins - sched_mins) <= 3:
                        return d["delay_seconds"]
                except ValueError:
                    pass

    return None
