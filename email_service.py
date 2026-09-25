import smtplib
from email.message import EmailMessage

import streamlit as st


def send_booking_confirmation(
    recipient_email,
    nome_farmacia,
    cap,
    start_datetime,
    end_datetime,
    durata,
    referente="",
):
    """
    Invia al cliente l'email di conferma della prenotazione
    utilizzando Gmail SMTP.
    """

    if not recipient_email or not recipient_email.strip():
        return False

    sender_email = st.secrets["gmail"]["sender_email"]
    app_password = st.secrets["gmail"]["app_password"]

    data = start_datetime.strftime("%d/%m/%Y")
    ora_inizio = start_datetime.strftime("%H:%M")
    ora_fine = end_datetime.strftime("%H:%M")

    subject = "Appuntamento confermato – Alessandro Iovine"

    if referente.strip():
        greeting = f"Buongiorno {referente.strip()},"
    else:
        greeting = "Buongiorno,"

    body = f"""{greeting}

la prenotazione è stata confermata.

DETTAGLI APPUNTAMENTO

Farmacia: {nome_farmacia}
Data: {data}
Orario: {ora_inizio} – {ora_fine}
Durata: {durata} minuti
CAP: {cap}

Appuntamento con:

Alessandro Iovine
Sales Manager
PIC · CONTROL · EFFERDENT

L'appuntamento è stato registrato correttamente.

A presto,
Alessandro Iovine
"""

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"Alessandro Iovine <{sender_email}>"
    message["To"] = recipient_email.strip()
    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=15,
    ) as smtp:
        smtp.login(
            sender_email,
            app_password,
        )
        smtp.send_message(message)

    return True
