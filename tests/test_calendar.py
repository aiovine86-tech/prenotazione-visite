from datetime import date
from unittest.mock import MagicMock, patch

from google_calendar import get_events, get_busy_slots


def test_reads_all_pages():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.side_effect = [
        {'items': [{'id': 'first'}], 'nextPageToken': 'next'},
        {'items': [{'id': 'second'}]},
    ]
    with patch('google_calendar.get_calendar_service', return_value=service), patch('google_calendar.get_calendar_id', return_value='test'):
        assert len(get_events(date(2026, 11, 9), date(2026, 11, 15))) == 2
    assert service.events.return_value.list.call_args.kwargs['pageToken'] == 'next'


def test_transparent_cancelled_and_all_day_events():
    events = [
        {'transparency': 'transparent'}, {'status': 'cancelled'},
        {'start': {'date': '2026-11-09'}, 'end': {'date': '2026-11-10'}},
    ]
    with patch('google_calendar.get_events', return_value=events):
        busy = get_busy_slots(date(2026, 11, 9), date(2026, 11, 15))
    assert len(busy) == 1
    assert busy[0]['end'].date() == date(2026, 11, 10)
