from datetime import datetime
from zoneinfo import ZoneInfo
import html

import streamlit as st

from booking import get_available_slots, format_slot
from google_calendar import create_appointment
from email_service import send_test_email


# =========================================================
# CONFIGURAZIONE
# =========================================================

TIMEZONE = ZoneInfo("Europe/Rome")

st.set_page_config(
    page_title="Prenota un appuntamento | Alessandro Iovine",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

if "prenotazione_completata" not in st.session_state:
    st.session_state.prenotazione_completata = False

if "ultima_prenotazione" not in st.session_state:
    st.session_state.ultima_prenotazione = None


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(52,199,89,.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(0,122,255,.10),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #f7faf8 0%,
            #f4f7fb 50%,
            #ffffff 100%
        );
}

.block-container {
    max-width: 720px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* HEADER */

.profile-header {
    text-align: center;
    margin-bottom: 2.4rem;
}

.profile-monogram {
    width: 74px;
    height: 74px;

    margin: 0 auto 18px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 24px;

    background: linear-gradient(
        135deg,
        #34c759 0%,
        #16a66a 45%,
        #007aff 100%
    );

    color: white;

    font-size: 26px;
    font-weight: 750;
    letter-spacing: -1px;

    box-shadow:
        0 14px 34px
        rgba(22,166,106,.22);
}

.booking-title {
    font-size: 34px;
    line-height: 1.1;

    font-weight: 750;
    letter-spacing: -1.2px;

    color: #111827;

    margin-bottom: 18px;
}

.profile-name {
    font-size: 21px;
    font-weight: 700;

    color: #111827;

    margin-bottom: 3px;
}

.profile-role {
    font-size: 15px;

    color: #667085;

    margin-bottom: 5px;
}

.profile-brands {
    font-size: 14px;
    font-weight: 650;

    color: #16864c;

    letter-spacing: .3px;

    margin-bottom: 18px;
}

.profile-description {
    max-width: 500px;

    margin: 0 auto;

    font-size: 16px;
    line-height: 1.55;

    color: #667085;
}


/* SEZIONI */

.section-header {
    display: flex;
    align-items: center;

    gap: 13px;

    margin-top: 32px;
    margin-bottom: 18px;
}

.section-number {
    min-width: 34px;
    width: 34px;
    height: 34px;

    border-radius: 12px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #34c759,
            #168f50
        );

    color: white;

    font-size: 14px;
    font-weight: 750;

    box-shadow:
        0 7px 16px
        rgba(52,199,89,.20);
}

.section-title {
    font-size: 19px;
    font-weight: 720;

    color: #111827;

    margin: 0;
}

.section-subtitle {
    font-size: 13px;

    color: #667085;

    margin-top: 2px;
}


/* INPUT */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,.96)
        !important;

    border-radius:
        14px
        !important;

    border:
        1px solid #e4e8ee
        !important;

    min-height: 48px;

    box-shadow:
        0 3px 10px
        rgba(16,24,40,.025);
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {

    border-color:
        #34c759
        !important;

    box-shadow:
        0 0 0 3px
        rgba(52,199,89,.10)
        !important;
}


/* DISPONIBILITÀ */

.availability-card {

    margin-top: 8px;
    margin-bottom: 18px;

    padding: 15px 17px;

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            rgba(52,199,89,.11),
            rgba(52,199,89,.045)
        );

    border:
        1px solid
        rgba(52,199,89,.20);

    color: #176c39;

    font-size: 14px;
    font-weight: 600;
}


/* BOTTONI */

div[data-testid="stButton"] button {

    min-height: 49px;

    border-radius:
        14px
        !important;

    font-weight:
        680
        !important;
}

div[data-testid="stButton"] button[kind="primary"] {

    background:
        linear-gradient(
            135deg,
            #34c759 0%,
            #209447 100%
        )
        !important;

    color:
        white
        !important;

    border:
        none
        !important;

    box-shadow:
        0 10px 24px
        rgba(32,148,71,.24)
        !important;
}

div[data-testid="stButton"] button[kind="secondary"] {

    background:
        white
        !important;

    color:
        #344054
        !important;

    border:
        1px solid #e4e7ec
        !important;
}


/* CONFERMA */

.success-card {

    margin-top: 20px;

    padding: 28px;

    border-radius: 24px;

    background:
        linear-gradient(
            145deg,
            rgba(52,199,89,.12),
            rgba(255,255,255,.92)
        );

    border:
        1px solid
        rgba(52,199,89,.22);

    box-shadow:
        0 18px 45px
        rgba(16,24,40,.06);
}

.success-icon {

    width: 52px;
    height: 52px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: #34c759;

    color: white;

    font-size: 26px;
    font-weight: 700;

    margin-bottom: 16px;
}

.success-title {

    font-size: 25px;
    font-weight: 750;

    color: #111827;

    margin-bottom: 8px;
}

.success-text {

    color: #667085;

    font-size: 15px;
    line-height: 1.55;

    margin-bottom: 20px;
}

.success-details {

    padding: 17px;

    border-radius: 16px;

    background:
        rgba(255,255,255,.82);

    color: #344054;

    line-height: 1.8;
}


/* FOOTER */

.footer-note {

    text-align: center;

    color: #667085;

    font-size: 12px;
    line-height: 1.5;

    margin-top: 34px;
}


/* TEST EMAIL */

.email-test-box {

    margin-top: 40px;

    padding: 22px;

    border-radius: 20px;

    background:
        rgba(255,255,255,.90);

    border:
        1px solid
        rgba(52,199,89,.20);

    box-shadow:
        0 8px 25px
        rgba(16,24,40,.05);
}

.email-test-title {

    color: #111827;

    font-size: 19px;
    font-weight: 720;

    margin-bottom: 5px;
}

.email-test-text {

    color: #667085;

    font-size: 14px;
    line-height: 1.5;
}


/* MOBILE */

@media (max-width: 640px) {

    .block-container {

        padding-top: 1.25rem;

        padding-left: 1rem;
        padding-right: 1rem;
    }

    .booking-title {

        font-size: 29px;
    }

    .profile-monogram {

        width: 66px;
        height: 66px;

        border-radius: 21px;

        font-size: 23px;
    }

    .profile-name {

        font-size: 19px;
    }

    .section-header {

        margin-top: 27px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# FUNZIONI UI
# =========================================================

def section_header(
    number,
    title,
    subtitle,
):

    markup = (
        '<div class="section-header">'
        f'<div class="section-number">{number}</div>'
        '<div>'
        f'<div class="section-title">{title}</div>'
        f'<div class="section-subtitle">{subtitle}</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        markup,
        unsafe_allow_html=True,
    )


def render_main_header():

    markup = (
        '<div class="profile-header">'
        '<div class="profile-monogram">AI</div>'
        '<div class="booking-title">'
        'Prenota un appuntamento'
        '</div>'
        '<div class="profile-name">'
        'Alessandro Iovine'
        '</div>'
        '<div class="profile-role">'
        'Sales Manager'
        '</div>'
        '<div class="profile-brands">'
        'PIC · CONTROL · EFFERDENT'
        '</div>'
        '<div class="profile-description">'
        'Scegli giorno e orario per fissare '
        'un appuntamento presso la tua farmacia.'
        '</div>'
        '</div>'
    )

    st.markdown(
        markup,
        unsafe_allow_html=True,
    )


def render_small_header():

    markup = (
        '<div class="profile-header">'
        '<div class="profile-monogram">AI</div>'
        '<div class="profile-name">'
        'Alessandro Iovine'
        '</div>'
        '<div class="profile-role">'
        'Sales Manager'
        '</div>'
        '<div class="profile-brands">'
        'PIC · CONTROL · EFFERDENT'
        '</div>'
        '</div>'
    )

    st.markdown(
        markup,
        unsafe_allow_html=True,
    )


# =========================================================
# SCHERMATA CONFERMA
# =========================================================

if st.session_state.prenotazione_completata:

    prenotazione = (
        st.session_state.ultima_prenotazione
    )

    nome_farmacia = html.escape(
        prenotazione["nome_farmacia"]
    )

    cap = html.escape(
        prenotazione["cap"]
    )

    data_testo = (
        prenotazione["start"]
        .strftime("%d/%m/%Y")
    )

    ora_testo = (
        prenotazione["start"]
        .strftime("%H:%M")
    )

    fine_testo = (
        prenotazione["end"]
        .strftime("%H:%M")
    )

    render_small_header()

    success_markup = (
        '<div class="success-card">'
        '<div class="success-icon">✓</div>'
        '<div class="success-title">'
        'Appuntamento confermato'
        '</div>'
        '<div class="success-text">'
        'Il tuo appuntamento con Alessandro Iovine '
        'è stato registrato correttamente.'
        '</div>'
        '<div class="success-details">'
        f'<strong>Farmacia:</strong> '
        f'{nome_farmacia}<br>'
        f'<strong>Data:</strong> '
        f'{data_testo}<br>'
        f'<strong>Orario:</strong> '
        f'{ora_testo} – {fine_testo}<br>'
        f'<strong>Durata:</strong> '
        f'{prenotazione["durata"]} minuti<br>'
        f'<strong>CAP:</strong> '
        f'{cap}'
        '</div>'
        '</div>'
    )

    st.markdown(
        success_markup,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button(
        "Prenota un altro appuntamento",
        use_container_width=True,
        type="primary",
    ):

        st.session_state.prenotazione_completata = False
        st.session_state.ultima_prenotazione = None

        st.rerun()

    st.stop()


# =========================================================
# HEADER
# =========================================================

render_main_header()


# =========================================================
# 1 - FARMACIA
# =========================================================

section_header(
    "1",
    "La tua farmacia",
    "Inserisci i dati principali",
)

nome_farmacia = st.text_input(
    "Nome farmacia *",
    placeholder="Es. Farmacia Centrale",
)

cap = st.text_input(
    "CAP *",
    placeholder="Es. 80100",
    max_chars=5,
)


# =========================================================
# 2 - APPUNTAMENTO
# =========================================================

section_header(
    "2",
    "Quando preferisci incontrarci?",
    "Scegli data, durata e orario",
)

durata = st.selectbox(
    "Durata dell'appuntamento",
    [
        30,
        45,
        60,
        75,
        90,
        105,
        120,
    ],
    index=3,
    format_func=lambda x: f"{x} minuti",
)

oggi = datetime.now(
    TIMEZONE
).date()

data = st.date_input(
    "Data",
    min_value=oggi,
    value=oggi,
)


# =========================================================
# DISPONIBILITÀ
# =========================================================

slots = []

if data.weekday() >= 5:

    st.warning(
        "Gli appuntamenti sono disponibili "
        "dal lunedì al venerdì."
    )

else:

    try:

        slots = get_available_slots(
            data,
            durata,
        )

        if data == oggi:

            now = datetime.now(
                TIMEZONE
            )

            slots = [
                slot
                for slot in slots
                if slot["start"] > now
            ]

    except Exception:

        slots = []

        st.error(
            "Non è stato possibile verificare "
            "la disponibilità del calendario."
        )


# =========================================================
# ORARIO
# =========================================================

selected_slot = None

if slots:

    availability_markup = (
        '<div class="availability-card">'
        f'✓ {len(slots)} orari disponibili '
        'per la durata selezionata'
        '</div>'
    )

    st.markdown(
        availability_markup,
        unsafe_allow_html=True,
    )

    selected_slot = st.selectbox(
        "Orario disponibile",
        slots,
        format_func=format_slot,
    )

elif data.weekday() < 5:

    st.info(
        "Nessun orario disponibile "
        "per la data e la durata selezionate."
    )


# =========================================================
# 3 - CONTATTI
# =========================================================

section_header(
    "3",
    "I tuoi contatti",
    "Facoltativi, ma utili per ricontattarti",
)

referente = st.text_input(
    "Referente",
    placeholder="Nome e cognome",
)

telefono = st.text_input(
    "Telefono",
    placeholder="Numero di telefono",
)

email = st.text_input(
    "Email",
    placeholder="nome@farmacia.it",
)


# =========================================================
# PRENOTAZIONE
# =========================================================

st.write("")

prenota = st.button(
    "Prenota appuntamento",
    type="primary",
    use_container_width=True,
    disabled=selected_slot is None,
)


if prenota:

    if not nome_farmacia.strip():

        st.error(
            "Inserisci il nome della farmacia."
        )

    elif not cap.strip():

        st.error(
            "Inserisci il CAP."
        )

    elif (
        not cap.isdigit()
        or len(cap) != 5
    ):

        st.error(
            "Inserisci un CAP valido "
            "di 5 cifre."
        )

    elif selected_slot is None:

        st.error(
            "Seleziona un orario disponibile."
        )

    else:

        try:

            # =============================================
            # RICONTROLLO DISPONIBILITÀ
            # =============================================

            updated_slots = (
                get_available_slots(
                    data,
                    durata,
                )
            )

            if data == oggi:

                now = datetime.now(
                    TIMEZONE
                )

                updated_slots = [
                    slot
                    for slot in updated_slots
                    if slot["start"] > now
                ]

            slot_still_available = any(

                slot["start"]
                == selected_slot["start"]

                and

                slot["end"]
                == selected_slot["end"]

                for slot in updated_slots
            )

            if not slot_still_available:

                st.warning(
                    "Questo orario è appena diventato "
                    "non disponibile. "
                    "Seleziona un altro orario."
                )

            else:

                # =========================================
                # GOOGLE CALENDAR
                # =========================================

                create_appointment(

                    nome_farmacia=
                        nome_farmacia.strip(),

                    cap=
                        cap.strip(),

                    start_datetime=
                        selected_slot["start"],

                    end_datetime=
                        selected_slot["end"],

                    durata=
                        durata,

                    referente=
                        referente.strip(),

                    telefono=
                        telefono.strip(),

                    email=
                        email.strip(),
                )

                # =========================================
                # SALVA CONFERMA
                # =========================================

                st.session_state.ultima_prenotazione = {

                    "nome_farmacia":
                        nome_farmacia.strip(),

                    "cap":
                        cap.strip(),

                    "start":
                        selected_slot["start"],

                    "end":
                        selected_slot["end"],

                    "durata":
                        durata,

                    "referente":
                        referente.strip(),

                    "telefono":
                        telefono.strip(),

                    "email":
                        email.strip(),
                }

                st.session_state.prenotazione_completata = True

                st.rerun()

        except Exception:

            st.error(
                "Non è stato possibile fissare "
                "l'appuntamento. Riprova."
            )


# =========================================================
# FOOTER
# =========================================================

footer_markup = (
    '<div class="footer-note">'
    'La prenotazione verrà registrata '
    'direttamente nel calendario di '
    'Alessandro Iovine.'
    '</div>'
)

st.markdown(
    footer_markup,
    unsafe_allow_html=True,
)


# =========================================================
# TEST EMAIL RESEND
# TEMPORANEO
# =========================================================

st.markdown(
    (
        '<div class="email-test-box">'
        '<div class="email-test-title">'
        'Test sistema email'
        '</div>'
        '<div class="email-test-text">'
        'Premi il pulsante qui sotto per verificare '
        'il collegamento tra questa applicazione '
        'e Resend.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

st.write("")

if st.button(
    "Invia email di prova",
    type="primary",
    use_container_width=True,
    key="test_resend_button",
):

    try:

        send_test_email()

        st.success(
            "Email inviata correttamente. "
            "Controlla la tua casella email "
            "e anche la cartella Spam."
        )

    except Exception as e:

        st.error(
            f"Errore Resend: {e}"
        )
