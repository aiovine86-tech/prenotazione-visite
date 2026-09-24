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


def get_available_slots(selected_date, duration_minutes):
    """
    Calcola gli orari disponibili per una determinata data
    e durata dell'appuntamento.
    """

    # 0 = lunedì, 6 = domenica
    if selected_date.weekday() >= 5:
        return []

    busy_slots = get_busy_slots(
        selected_date,
        selected_date
    )

    available_slots = []

    duration = timedelta(minutes=duration_minutes)
    buffer_time = timedelta(minutes=BUFFER_MINUTES)

    for period_start, period_end in WORKING_PERIODS:

        current = datetime.combine(
            selected_date,
            period_start,
            tzinfo=TIMEZONE
        )

        working_end = datetime.combine(
            selected_date,
            period_end,
            tzinfo=TIMEZONE
        )

        # Proponiamo partenze ogni 15 minuti.
        while current + duration <= working_end:

            appointment_end = current + duration

            slot_valid = True

            for busy in busy_slots:

                busy_start = busy["start"].astimezone(TIMEZONE)
                busy_end = busy["end"].astimezone(TIMEZONE)

                # Proteggiamo 15 minuti prima e dopo
                # ciascun appuntamento già presente.
                protected_start = busy_start - buffer_time
                protected_end = busy_end + buffer_time

                if _overlaps(
                    current,
                    appointment_end,
                    protected_start,
                    protected_end
                ):
                    slot_valid = False
                    break

            if slot_valid:
                available_slots.append(
                    {
                        "start": current,
                        "end": appointment_end
                    }
                )

            current += timedelta(minutes=15)

    return available_slots


def format_slot(slot):
    return (
        f"{slot['start'].strftime('%H:%M')} – "
        f"{slot['end'].strftime('%H:%M')}"
    )
