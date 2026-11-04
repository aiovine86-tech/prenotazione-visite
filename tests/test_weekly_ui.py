from datetime import datetime, timedelta
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from booking import TIMEZONE


def test_week_navigation_selection_duration_and_api_failure():
    source = '''
from datetime import date
import streamlit as st
from weekly_calendar import render_weekly_calendar
from tests.test_weekly_ui import busy
@st.cache_data
def load_busy(start, end):
    return busy(start, end)
duration = st.selectbox('Durata', [30, 75])
slot = render_weekly_calendar(duration, date(2026, 11, 9), 'Farmacia', '81030', 'Lusciano', load_busy, lambda *a: [])
if slot:
    st.write('CHOSEN ' + slot['start'].isoformat())
'''
    at = AppTest.from_string(source, default_timeout=30).run()
    assert not at.exception
    assert any(b.disabled and 'Occupato' in b.label for b in at.button)
    available = next(b for b in at.button if 'Disponibile' in b.label and not b.disabled)
    available.click().run()
    assert not at.exception
    assert any('CHOSEN' in m.value for m in at.markdown)
    at.selectbox[0].select(75).run()
    assert not any('CHOSEN' in m.value for m in at.markdown)
    next(b for b in at.button if b.label == 'Successiva →').click().run()
    assert any('16/11/2026' in m.value for m in at.markdown)
    previous = next(b for b in at.button if b.label == '← Precedente')
    assert not previous.disabled
    previous.click().run()
    assert any('09/11/2026' in m.value for m in at.markdown)
    with patch('tests.test_weekly_ui.busy', side_effect=RuntimeError('offline')):
        next(b for b in at.button if b.label == 'Aggiorna disponibilità').click().run()
    assert at.error
    assert not any('Disponibile' in b.label for b in at.button)


def busy(start, end):
    return [{'start': datetime(2026, 11, 9, 10, tzinfo=TIMEZONE),
             'end': datetime(2026, 11, 9, 11, tzinfo=TIMEZONE)}]


def test_full_app_without_pharmacy_does_not_read_calendar():
    with patch('google_calendar.get_busy_slots') as read:
        at = AppTest.from_file('../app.py', default_timeout=30).run()
    assert not at.exception
    read.assert_not_called()
    assert any('CAP e farmacia' in x.value for x in at.info)
