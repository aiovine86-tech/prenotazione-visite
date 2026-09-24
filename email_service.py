import streamlit as st
import resend


def send_test_email():
    """
    Invia una mail di prova all'indirizzo configurato
    nei Secrets di Streamlit.
    """

    resend.api_key = st.secrets["resend"]["api_key"]

    destinatario = st.secrets["resend"]["test_email"]

    params = {
        "from": "Alessandro Iovine <onboarding@resend.dev>",
        "to": [destinatario],
        "subject": "Test prenotazione appuntamenti",
        "html": """
        <div style="
            font-family: Arial, Helvetica, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
        ">

            <h2 style="margin-bottom: 8px;">
                Test email riuscito
            </h2>

            <p>
                Questa email è stata inviata dalla tua
                applicazione di prenotazione appuntamenti.
            </p>

            <p>
                Se stai leggendo questo messaggio,
                il collegamento tra Streamlit e Resend
                funziona correttamente.
            </p>

            <hr style="
                border: 0;
                border-top: 1px solid #eeeeee;
                margin: 30px 0;
            ">

            <p style="
                color: #666666;
                font-size: 14px;
            ">
                Alessandro Iovine<br>
                Sales Manager<br>
                PIC · CONTROL · EFFERDENT
            </p>

        </div>
        """,
    }

    return resend.Emails.send(params)
