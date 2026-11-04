"""Weekly booking UI; all availability comes from booking.py and Calendar."""
from datetime import timedelta

import streamlit as st

from booking import get_day_slots, format_slot, WORKING_PERIODS

MONTHS = ('gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic')

DAYS = ('Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica')


def render_weekly_calendar(duration, today, pharmacy, cap, town, load_busy, recommend):
    monday = today - timedelta(days=today.weekday())
    st.session_state.setdefault('weekly_start', monday)
    context = (duration, pharmacy, cap, town)
    if st.session_state.get('weekly_context') != context:
        st.session_state.pop('weekly_selected', None)
        st.session_state.weekly_context = context

    st.markdown('''<style>
    .st-key-weekly_calendar {background:#fff; padding:16px; border:1px solid #e4e7ec;
        border-radius:18px; color:#24343a;}
    .st-key-weekly_calendar button:disabled {background:#eee!important;color:#61676c!important;
        opacity:1!important;border:1px solid #ddd!important;}
    .week-day {background:#eff3f2;padding:12px;border-radius:8px;color:#286461;
        font-weight:750;margin-top:12px;}
    .week-legend {font-size:13px;color:#475467;margin:4px 0 10px;}
    .week-range {font-size:18px;font-weight:750;color:#24343a;margin:0 0 8px;}
    .week-range small {display:block;font-size:12px;font-weight:500;color:#667085;margin-bottom:2px;}
    .st-key-week_navigation [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important;gap:6px!important;}
    .st-key-week_navigation [data-testid="stColumn"] {min-width:0!important;flex:1 1 0!important;}
    .st-key-week_navigation button {min-height:42px!important;padding:6px 8px!important;
        border-radius:10px!important;box-shadow:none!important;}
    .st-key-week_navigation button p {font-size:12px!important;line-height:1.25!important;}
    .st-key-week_refresh button {min-height:32px!important;padding:4px 8px!important;
        font-size:12px!important;border:0!important;box-shadow:none!important;}

    @media(max-width:640px){.st-key-weekly_calendar{padding:10px;}}
    </style>''', unsafe_allow_html=True)

    with st.container(key='weekly_calendar'):
        st.markdown('### Scegli un orario')
        st.caption('Seleziona un orario verde. La prenotazione viene confermata direttamente, senza registrazione.')
        st.markdown('<div class="week-legend">🟢 Disponibile · ⚪ Non disponibile</div>',
                    unsafe_allow_html=True)
        start = st.session_state.weekly_start
        end = start + timedelta(days=6)
        date_range = f'{start.day} {MONTHS[start.month - 1]} – {end.day} {MONTHS[end.month - 1]} {end.year}'
        if start.year != end.year:
            date_range = f'{start.day} {MONTHS[start.month - 1]} {start.year} – {end.day} {MONTHS[end.month - 1]} {end.year}'
        st.markdown(f'<div class="week-range"><small>Settimana visualizzata</small>{date_range}</div>',
                    unsafe_allow_html=True)
        with st.container(key='week_navigation'):
            prev, current, nxt = st.columns(3, gap='small')
            if prev.button('← Settimana', disabled=start <= monday,
                           help='Vai alla settimana precedente', use_container_width=True):
                st.session_state.weekly_start -= timedelta(days=7)
                st.session_state.pop('weekly_selected', None)
                st.rerun()
            if current.button('Questa settimana', disabled=start == monday,
                              help='Torna alla settimana attuale', use_container_width=True):
                st.session_state.weekly_start = monday
                st.session_state.pop('weekly_selected', None)
                st.rerun()
            if nxt.button('Settimana →', help='Vai alla settimana successiva', use_container_width=True):
                st.session_state.weekly_start += timedelta(days=7)
                st.session_state.pop('weekly_selected', None)
                st.rerun()
        with st.container(key='week_refresh'):
            if st.button('↻ Aggiorna disponibilità'):
                load_busy.clear()
        if not (pharmacy.strip() and cap and town):
            st.info('Inserisci CAP e farmacia per visualizzare le disponibilità reali.')
            return None
        try:
            busy = load_busy(start - timedelta(days=1), end + timedelta(days=1))
        except Exception:
            st.error('Disponibilità non verificabile. Riprova con Aggiorna disponibilità.')
            return None

        suggestions = recommend(cap, town, duration, today)
        suggested = {r['data']: r for r in suggestions}
        if suggestions:
            st.caption('Date consigliate: ' + ' · '.join(f"{r['data']:%d/%m}" for r in suggestions)
                       + ' (visite già in zona). Tutti gli orari verdi restano prenotabili.')
        else:
            st.caption('Nessuna data consigliata con visite vicine nei prossimi 7 giorni.')

        selected = None
        for offset in range(7):
            day = start + timedelta(days=offset)
            if day < today:
                continue
            suffix = ' · Consigliato in zona' if day in suggested else ''
            st.markdown(f'<div class="week-day">{DAYS[day.weekday()]} · {day:%d/%m/%Y}{suffix}</div>',
                        unsafe_allow_html=True)
            if day.weekday() >= 5:
                st.caption('Chiuso · appuntamenti dal lunedì al venerdì')
                continue
            candidates = [slot for slot in get_day_slots(day, duration, busy)
                          if slot['reason'] != 'Trascorso']
            if not candidates:
                st.caption('Nessun altro orario per oggi.')
                continue
            for period_start, period_end in WORKING_PERIODS:
                period = [s for s in candidates if period_start <= s['start'].time() < period_end]
                if not period:
                    continue
                st.caption(f'{period_start:%H:%M} – {period_end:%H:%M}')
                # Two columns remain comfortably tappable on phones; Streamlit stacks on narrow screens.
                for row in range(0, len(period), 2):
                    for column, slot in zip(st.columns(2), period[row:row + 2]):
                        token = slot['start'].isoformat()
                        active = st.session_state.get('weekly_selected') == token
                        label = format_slot(slot)
                        label += ' · ' + (slot['reason'] or ('✓ Selezionato' if active else 'Disponibile'))
                        if column.button(label, key='slot_' + token,
                                         type='secondary' if slot['reason'] else 'primary',
                                         disabled=bool(slot['reason']), use_container_width=True):
                            st.session_state.weekly_selected = token
                            st.rerun()
                        if not slot['reason'] and st.session_state.get('weekly_selected') == token:
                            selected = {'start': slot['start'], 'end': slot['end']}
        if selected:
            st.success(f"Selezionato: {selected['start']:%d/%m/%Y} · {format_slot(selected)}")
        else:
            st.caption('Seleziona un orario disponibile per continuare.')
        return selected
