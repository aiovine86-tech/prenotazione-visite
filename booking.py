from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from google_calendar import get_busy_slots


TIMEZONE = ZoneInfo("Europe/Rome")
BUFFER_MINUTES = 15

WORKING_PERIODS = [
    (time(8, 30), time(13, 0)),
    (time(14, 30), time(17, 30)),
]


def _overlaps(start_a, end_a, start_b, end_b):
    return start_a < end_b and end_a > start_b


def get_day_slots(selected_date, duration_minutes, busy_slots, now=None):
    """All candidate starts, with a reason when they cannot be booked."""
    if selected_date.weekday() >= 5:
        return []
    if duration_minutes not in range(30, 121, 15):
        raise ValueError("Durata non valida")
    now = now or datetime.now(TIMEZONE)
    duration = timedelta(minutes=duration_minutes)
    buffer_time = timedelta(minutes=BUFFER_MINUTES)
    slots = []
    for period_start, period_end in WORKING_PERIODS:
        current = datetime.combine(selected_date, period_start, tzinfo=TIMEZONE)
        working_end = datetime.combine(selected_date, period_end, tzinfo=TIMEZONE)
        while current + duration <= working_end:
            end = current + duration
            reason = ""
            if current <= now:
                reason = "Trascorso"
            elif any(_overlaps(current, end, b["start"], b["end"]) for b in busy_slots):
                reason = "Occupato"
            elif any(_overlaps(current, end, b["start"] - buffer_time,
                               b["end"] + buffer_time) for b in busy_slots):
                reason = "Pausa tra visite"
            slots.append({"start": current, "end": end, "reason": reason})
            current += timedelta(minutes=15)
    return slots


def get_available_slots(selected_date, duration_minutes, busy_slots=None):
    """Fresh Calendar read by default, including the final booking check."""
    if selected_date.weekday() >= 5:
        return []
    if busy_slots is None:
        # Include adjacent days so the 15-minute buffer also crosses midnight.
        busy_slots = get_busy_slots(selected_date - timedelta(days=1),
                                    selected_date + timedelta(days=1))
    return [{"start": s["start"], "end": s["end"]}
            for s in get_day_slots(selected_date, duration_minutes, busy_slots)
            if not s["reason"]]


def format_slot(slot):
    return (
        f"{slot['start'].strftime('%H:%M')} – "
        f"{slot['end'].strftime('%H:%M')}"
    )
