from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE_NAME = "Europe/Rome"
TIMEZONE = ZoneInfo(TIMEZONE_NAME)


# --------------------------------------------------
# CONNESSIONE GOOGLE CALENDAR
# --------------------------------------------------

def get_calendar_service():

    credentials_info = dict(
        st.secrets["gcp_service_account"]
    )

    credentials = (
        service_account.Credentials
        .from_service_account_info(
            credentials_info,
            scopes=SCOPES
        )
    )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )


def get_calendar_id():

    return st.secrets["calendar"]["id"]


# --------------------------------------------------
# LETTURA EVENTI
# --------------------------------------------------

def get_events(start_date, end_date):

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=TIMEZONE
    )

    end_datetime = datetime.combine(
        end_date,
        datetime.max.time(),
        tzinfo=TIMEZONE
    )

    result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_datetime.isoformat(),
        timeMax=end_datetime.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return result.get("items", [])


# --------------------------------------------------
# FASCE OCCUPATE
# --------------------------------------------------

def get_busy_slots(start_date, end_date):

    events = get_events(
        start_date,
        end_date
    )

    busy_slots = []

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        # Ignoriamo per ora eventi giornalieri
        if (
            "dateTime" not in start
            or "dateTime" not in end
        ):
            continue

        start_dt = datetime.fromisoformat(
            start["dateTime"].replace(
                "Z",
                "+00:00"
            )
        )

        end_dt = datetime.fromisoformat(
            end["dateTime"].replace(
                "Z",
                "+00:00"
            )
        )

        busy_slots.append(
            {
                "start": start_dt,
                "end": end_dt
            }
        )

    return busy_slots


# --------------------------------------------------
# CREA APPUNTAMENTO
# --------------------------------------------------

def create_appointment(
    nome_farmacia,
    cap,
    start_datetime,
    end_datetime,
    durata,
    referente="",
    telefono="",
    email=""
):

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    descrizione = [
        f"Farmacia: {nome_farmacia}",
        f"CAP: {cap}",
        f"Durata: {durata} minuti"
    ]

    if referente.strip():
        descrizione.append(
            f"Referente: {referente.strip()}"
        )

    if telefono.strip():
        descrizione.append(
            f"Telefono: {telefono.strip()}"
        )

    if email.strip():
        descrizione.append(
            f"Email: {email.strip()}"
        )

    event = {
        "summary": f"Visita - {nome_farmacia}",
        "description": "\n".join(
            descrizione
        ),
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": TIMEZONE_NAME
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": TIMEZONE_NAME
        }
    }

    created_event = (
        service.events()
        .insert(
            calendarId=calendar_id,
            body=event
        )
        .execute()
    )

    return created_event


# --------------------------------------------------
# TEST
# --------------------------------------------------

def test_connection():

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    calendar = (
        service.calendars()
        .get(
            calendarId=calendar_id
        )
        .execute()
    )

    return calendar.get(
        "summary",
        "Calendario collegato"
    )
