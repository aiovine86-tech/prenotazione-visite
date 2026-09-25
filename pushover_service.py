import urllib.parse
import urllib.request

import streamlit as st


def send_booking_notification(
    nome_farmacia,
    cap,
    start_datetime,
    durata,
    referente="",
):
    """
    Invia una notifica Pushover.
    Se Pushover non risponde, genera un'eccezione che verrà
    gestita separatamente dall'app.
    """

    user_key = st.secrets["pushover"]["user_key"]
    api_token = st.secrets["pushover"]["api_token"]

    data_ora = start_datetime.strftime("%d/%m/%Y · %H:%M")

    message_lines = [
        f"Farmacia: {nome_farmacia}",
        f"Data: {data_ora}",
        f"Durata: {durata} min",
        f"CAP: {cap}",
    ]

    if referente.strip():
        message_lines.append(f"Referente: {referente.strip()}")

    payload = urllib.parse.urlencode(
        {
            "token": api_token,
            "user": user_key,
            "title": "Nuova prenotazione",
            "message": "\n".join(message_lines),
            "sound": "pushover",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.pushover.net/1/messages.json",
        data=payload,
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")
