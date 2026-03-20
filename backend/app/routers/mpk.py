from fastapi import APIRouter

from backend.app.core.mpk_config import COMMUTES, NEXT_DEPARTURES_COUNT
from backend.app.services.gtfs_rt import fetch_rt_delays, get_delay_for_departure
from backend.app.services.mpk_scraper import get_next_departures

router = APIRouter(prefix="/api/mpk", tags=["mpk"])


async def _enrich_with_delays(commute_id: str, line_name: str, departures: list) -> list:
    """Add delay_seconds to each departure from GTFS-RT data."""
    for dep in departures:
        delay = get_delay_for_departure(line_name, commute_id, dep.get("time", ""))
        dep["delay_seconds"] = delay  # None = no data, 0 = on time, >0 = late, <0 = early
    return departures


@router.get("/departures")
async def departures():
    """Get next departures for all configured commutes, enriched with RT delays."""
    await fetch_rt_delays()

    results = []
    for commute in COMMUTES:
        commute_data = {
            "id": commute["id"],
            "label": commute["label"],
            "lines": [],
        }

        for line_cfg in commute["lines"]:
            next_deps = await get_next_departures(
                line_id=line_cfg["line_id"],
                timetable_id=line_cfg["timetable_id"],
                direction=line_cfg["direction"],
                stop_number=line_cfg["stop_number"],
                count=NEXT_DEPARTURES_COUNT,
            )
            await _enrich_with_delays(commute["id"], line_cfg["line_name"], next_deps)
            commute_data["lines"].append({
                "line_name": line_cfg["line_name"],
                "stop_name": line_cfg["stop_name"],
                "departures": next_deps,
            })

        results.append(commute_data)

    return {"commutes": results}


@router.get("/departures/{commute_id}")
async def departures_by_commute(commute_id: str):
    """Get next departures for a specific commute."""
    await fetch_rt_delays()

    commute = next((c for c in COMMUTES if c["id"] == commute_id), None)
    if not commute:
        return {"error": "Commute not found"}

    lines = []
    for line_cfg in commute["lines"]:
        next_deps = await get_next_departures(
            line_id=line_cfg["line_id"],
            timetable_id=line_cfg["timetable_id"],
            direction=line_cfg["direction"],
            stop_number=line_cfg["stop_number"],
            count=NEXT_DEPARTURES_COUNT,
        )
        await _enrich_with_delays(commute["id"], line_cfg["line_name"], next_deps)
        lines.append({
            "line_name": line_cfg["line_name"],
            "stop_name": line_cfg["stop_name"],
            "departures": next_deps,
        })

    return {"id": commute["id"], "label": commute["label"], "lines": lines}
