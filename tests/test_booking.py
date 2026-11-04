from datetime import date, datetime, timedelta
from unittest.mock import patch

from booking import TIMEZONE, get_day_slots, get_available_slots

DAY = date(2026, 11, 9)
NOW = datetime(2026, 11, 8, tzinfo=TIMEZONE)


def dt(hour, minute=0):
    return datetime(2026, 11, 9, hour, minute, tzinfo=TIMEZONE)


def test_buffer_and_exact_boundaries():
    busy = [{'start': dt(10), 'end': dt(11)}]
    slots = {s['start']: s for s in get_day_slots(DAY, 30, busy, NOW)}
    assert slots[dt(9, 15)]['reason'] == ''
    assert slots[dt(9, 30)]['reason'] == 'Pausa tra visite'
    assert slots[dt(10)]['reason'] == 'Occupato'
    assert slots[dt(11)]['reason'] == 'Pausa tra visite'
    assert slots[dt(11, 15)]['reason'] == ''


def test_periods_durations_weekend_and_past():
    for duration in range(30, 121, 15):
        slots = get_day_slots(DAY, duration, [], NOW)
        assert all(s['end'] - s['start'] == timedelta(minutes=duration) for s in slots)
        assert all(s['end'] <= dt(13) or (s['start'] >= dt(14, 30) and s['end'] <= dt(17, 30)) for s in slots)
    assert get_day_slots(date(2026, 11, 14), 30, [], NOW) == []
    assert all(s['reason'] == 'Trascorso' for s in get_day_slots(DAY, 30, [], dt(18)))


def test_all_day_event_blocks_day():
    busy = [{'start': dt(0), 'end': dt(0) + timedelta(days=1)}]
    assert all(s['reason'] == 'Occupato' for s in get_day_slots(DAY, 75, busy, NOW))


def test_final_check_reads_fresh_and_propagates_failure():
    import pytest
    with patch('booking.get_busy_slots', side_effect=RuntimeError('offline')) as read:
        with pytest.raises(RuntimeError):
            get_available_slots(DAY, 75)
        read.assert_called_once()
    with patch('booking.get_busy_slots') as read:
        get_available_slots(DAY, 75, [])
        read.assert_not_called()
