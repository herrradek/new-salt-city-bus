# =============================================================
# MPK Łódź Bus Tracking Configuration
# =============================================================
# Data source: https://mpk.lodz.pl/rozklady/
#
# To find stop IDs: go to trasa.jsp?lineId=<ID>, click a stop,
# and check the "stopNumber" param in the URL.
#
# Line IDs:  53A = 501,  53B = 744
# Direction 1 = outbound (Fabryczna → Nowosolna / Brzeziny)
# Direction 2 = inbound  (Nowosolna / Brzeziny → Fabryczna)
#
# NOTE: The same physical stop can have DIFFERENT stopNumber
# values depending on line and direction.
# =============================================================

MPK_BASE_URL = "https://mpk.lodz.pl/rozklady"

# --- Commute definitions ---
COMMUTES = [
    {
        "id": "home_to_office",
        "label": "Home → Office",
        "lines": [
            {
                "line_name": "53A",
                "line_id": 501,
                "timetable_id": 1,
                "direction": 2,            # inbound → Fabryczna
                "stop_number": 72,          # Hiacyntowa NŻ
                "stop_name": "Hiacyntowa NŻ",
            },
            {
                "line_name": "53B",
                "line_id": 744,
                "timetable_id": 1,
                "direction": 2,            # inbound → Fabryczna
                "stop_number": 72,          # Hiacyntowa NŻ
                "stop_name": "Hiacyntowa NŻ",
            },
        ],
    },
    {
        "id": "office_to_home",
        "label": "Office → Home",
        "lines": [
            {
                "line_name": "53A",
                "line_id": 501,
                "timetable_id": 1,
                "direction": 1,            # outbound → Nowosolna
                "stop_number": 2158,        # Rodziny Poznańskich - Dw. Łódź Fabryczna
                "stop_name": "Dw. Łódź Fabryczna",
            },
            {
                "line_name": "53B",
                "line_id": 744,
                "timetable_id": 1,
                "direction": 1,            # outbound → Brzeziny
                "stop_number": 2158,        # Rodziny Poznańskich - Dw. Łódź Fabryczna
                "stop_name": "Dw. Łódź Fabryczna",
            },
        ],
    },
]

# How many upcoming departures to show per line
NEXT_DEPARTURES_COUNT = 5

# Cache timetable data for this many seconds
CACHE_TTL_SECONDS = 3600  # 1 hour
