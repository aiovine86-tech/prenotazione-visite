from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build


# =========================================================
# CONFIGURAZIONE
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

TIMEZONE_NAME = "Europe/Rome"
TIMEZONE = ZoneInfo(TIMEZONE_NAME)


# =========================================================
# CONNESSIONE GOOGLE CALENDAR
# =========================================================

@st.cache_resource
def get_calendar_service():

    credentials_info = dict(
        st.secrets["gcp_service_account"]
    )

    credentials = (
        service_account.Credentials
        .from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )
    )

    service = build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )

    return service


# =========================================================
# CALENDAR ID
# =========================================================

def get_calendar_id():

    return st.secrets[
        "calendar"
    ]["id"]


# =========================================================
# LETTURA EVENTI
# =========================================================

def get_events(
    start_date,
    end_date,
):

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=TIMEZONE,
    )

    end_datetime = datetime.combine(
        end_date,
        datetime.max.time(),
        tzinfo=TIMEZONE,
    )

    result = (
        service
        .events()
        .list(
            calendarId=calendar_id,
            timeMin=start_datetime.isoformat(),
            timeMax=end_datetime.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return result.get(
        "items",
        [],
    )


# =========================================================
# FASCE OCCUPATE
# =========================================================

def get_busy_slots(
    start_date,
    end_date,
):

    events = get_events(
        start_date,
        end_date,
    )

    busy_slots = []

    for event in events:

        start = event.get(
            "start",
            {},
        )

        end = event.get(
            "end",
            {},
        )

        # -------------------------------------------------
        # EVENTO CON ORARIO
        # -------------------------------------------------

        if (
            "dateTime" in start
            and
            "dateTime" in end
        ):

            start_dt = datetime.fromisoformat(
                start["dateTime"].replace(
                    "Z",
                    "+00:00",
                )
            )

            end_dt = datetime.fromisoformat(
                end["dateTime"].replace(
                    "Z",
                    "+00:00",
                )
            )

            busy_slots.append(
                {
                    "start": start_dt,
                    "end": end_dt,
                }
            )

        # -------------------------------------------------
        # EVENTO GIORNALIERO
        # -------------------------------------------------

        elif (
            "date" in start
            and
            "date" in end
        ):

            start_date_event = (
                datetime
                .fromisoformat(
                    start["date"]
                )
                .date()
            )

            end_date_event = (
                datetime
                .fromisoformat(
                    end["date"]
                )
                .date()
            )

            start_dt = datetime.combine(
                start_date_event,
                datetime.min.time(),
                tzinfo=TIMEZONE,
            )

            # Google Calendar considera la data finale
            # dell'evento giornaliero esclusiva.
            end_dt = datetime.combine(
                end_date_event,
                datetime.min.time(),
                tzinfo=TIMEZONE,
            )

            busy_slots.append(
                {
                    "start": start_dt,
                    "end": end_dt,
                }
            )

    return busy_slots


# =========================================================
# LETTURA CAMPI DALLA DESCRIZIONE
# =========================================================

def _get_description_value(
    description,
    field_name,
):

    if not description:
        return ""

    prefix = f"{field_name}:"

    for line in description.splitlines():

        line = line.strip()

        if line.lower().startswith(
            prefix.lower()
        ):

            return line[
                len(prefix):
            ].strip()

    return ""


# =========================================================
# APPUNTAMENTI CON INFORMAZIONI TERRITORIALI
# =========================================================

def get_territorial_appointments(
    start_date,
    end_date,
):
    """
    Restituisce gli eventi del calendario con le informazioni
    necessarie per calcolare le date consigliate.

    Gli eventi senza CAP/Comune continuano normalmente a bloccare
    gli slot tramite get_busy_slots(), ma non vengono usati per
    stabilire la vicinanza territoriale.
    """

    events = get_events(
        start_date,
        end_date,
    )

    appointments = []

    for event in events:

        start = event.get(
            "start",
            {},
        )

        end = event.get(
            "end",
            {},
        )

        # Gli eventi giornalieri non rappresentano
        # una visita territoriale.
        if (
            "dateTime" not in start
            or
            "dateTime" not in end
        ):
            continue

        try:

            start_dt = datetime.fromisoformat(
                start["dateTime"].replace(
                    "Z",
                    "+00:00",
                )
            ).astimezone(TIMEZONE)

            end_dt = datetime.fromisoformat(
                end["dateTime"].replace(
                    "Z",
                    "+00:00",
                )
            ).astimezone(TIMEZONE)

        except (ValueError, TypeError):
            continue

        description = event.get(
            "description",
            "",
        )

        cap = _get_description_value(
            description,
            "CAP",
        )

        comune = _get_description_value(
            description,
            "Comune",
        )

        farmacia = _get_description_value(
            description,
            "Farmacia",
        )

        if not farmacia:
            farmacia = event.get(
                "summary",
                "",
            )

        appointments.append(
            {
                "start": start_dt,
                "end": end_dt,
                "cap": cap,
                "comune": comune,
                "farmacia": farmacia,
            }
        )

    return appointments


# =========================================================
# CREA APPUNTAMENTO
# =========================================================

def create_appointment(
    nome_farmacia,
    cap,
    comune,
    start_datetime,
    end_datetime,
    durata,
    referente="",
    telefono="",
    email="",
):

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    # -----------------------------------------------------
    # DESCRIZIONE
    # -----------------------------------------------------

    descrizione = [
        "Appuntamento con Alessandro Iovine",
        "Sales Manager",
        "PIC · CONTROL · EFFERDENT",
        "",
        f"Farmacia: {nome_farmacia}",
        f"CAP: {cap}",
        f"Comune: {comune}",
        f"Durata: {durata} minuti",
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

    # -----------------------------------------------------
    # EVENTO
    # -----------------------------------------------------

    event = {

        # Nel calendario viene visualizzato
        # il nome della farmacia.
        "summary": nome_farmacia,

        "description":
            "\n".join(descrizione),

        "start": {
            "dateTime":
                start_datetime.isoformat(),

            "timeZone":
                TIMEZONE_NAME,
        },

        "end": {
            "dateTime":
                end_datetime.isoformat(),

            "timeZone":
                TIMEZONE_NAME,
        },

        "reminders": {
            "useDefault": False,

            "overrides": [
                {
                    "method": "popup",
                    "minutes": 30,
                }
            ],
        },
    }

    # -----------------------------------------------------
    # CREA EVENTO
    # -----------------------------------------------------

    created_event = (
        service
        .events()
        .insert(
            calendarId=calendar_id,
            body=event,
        )
        .execute()
    )

    return created_event


# =========================================================
# TEST CONNESSIONE
# =========================================================

def test_connection():

    service = get_calendar_service()
    calendar_id = get_calendar_id()

    calendar = (
        service
        .calendars()
        .get(
            calendarId=calendar_id
        )
        .execute()
    )

    return calendar.get(
        "summary",
        "Calendario collegato",
    )
