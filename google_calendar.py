from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Europe/Rome"


def get_calendar_service():
    """
    Crea il collegamento autenticato con Google Calendar.
    Le credenziali vengono lette esclusivamente dai Secrets di Streamlit.
    """

    credentials_info = dict(st.secrets["gcp_service_account"])

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

    service = build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )

    return service


def get_calendar_id():
    return st.secrets["calendar"]["id"]


def get_events(start_date, end_date):
    """
    Restituisce gli eventi presenti nel calendario
    tra start_date e end_date.
    """

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    tz = ZoneInfo(TIMEZONE)

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=tz
    )

    end_datetime = datetime.combine(
        end_date,
        datetime.max.time(),
        tzinfo=tz
    )

    result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_datetime.isoformat(),
        timeMax=end_datetime.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return result.get("items", [])


def get_busy_slots(start_date, end_date):
    """
    Converte gli eventi Google Calendar
    in fasce orarie occupate.

    Non restituisce al cliente titolo, farmacia
    o altri dettagli dell'evento.
    """

    events = get_events(start_date, end_date)

    busy_slots = []

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        # Ignoriamo per ora gli eventi che durano tutto il giorno.
        if "dateTime" not in start or "dateTime" not in end:
            continue

        start_dt = datetime.fromisoformat(
            start["dateTime"].replace("Z", "+00:00")
        )

        end_dt = datetime.fromisoformat(
            end["dateTime"].replace("Z", "+00:00")
        )

        busy_slots.append(
            {
                "start": start_dt,
                "end": end_dt
            }
        )

    return busy_slots


def test_connection():
    """
    Test semplice per verificare che Streamlit
    riesca ad accedere a Visite Farmacie.
    """

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    calendar = service.calendars().get(
        calendarId=calendar_id
    ).execute()

    return calendar.get("summary", "Calendario collegato")
