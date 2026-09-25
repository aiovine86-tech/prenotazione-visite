from datetime import datetime
from zoneinfo import ZoneInfo
import html

import streamlit as st

from booking import get_available_slots, format_slot
from google_calendar import create_appointment
from pushover_service import send_booking_notification
from email_service import send_booking_confirmation


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
# CSS — APPLE / iOS STYLE
# =========================================================

st.markdown(
    """
<style>

/* ========================================================
   BASE
   ======================================================== */

.stApp {
    background:
        radial-gradient(
            circle at 8% -5%,
            rgba(52,199,89,.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 100% 5%,
            rgba(0,122,255,.08),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #f7f9fb 0%,
            #f4f6f8 45%,
            #ffffff 100%
        );
}

.block-container {
    max-width: 680px;
    padding-top: 1.6rem;
    padding-bottom: 3.5rem;
}


/* Nasconde elementi Streamlit non necessari */

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ========================================================
   HEADER
   ======================================================== */

.profile-header {
    text-align: center;
    margin-bottom: 2rem;
}

.profile-monogram {
    width: 68px;
    height: 68px;

    margin: 0 auto 17px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 21px;

    background:
        linear-gradient(
            135deg,
            #34c759 0%,
            #18a45f 48%,
            #007aff 100%
        );

    color: white;

    font-size: 24px;
    font-weight: 760;
    letter-spacing: -1px;

    box-shadow:
        0 12px 30px
        rgba(20,150,80,.20);
}

.booking-title {
    font-size: 32px;
    line-height: 1.12;

    font-weight: 760;
    letter-spacing: -1.15px;

    color: #101828;

    margin-bottom: 10px;
}

.profile-description {
    max-width: 460px;

    margin:
        0 auto;

    font-size: 15px;
    line-height: 1.55;

    color: #667085;
}


/* ========================================================
   PROFILO
   ======================================================== */

.profile-card {
    display: inline-flex;
    align-items: center;

    gap: 12px;

    margin-top: 20px;

    padding:
        10px 15px
        10px 10px;

    border-radius: 18px;

    background:
        rgba(255,255,255,.82);

    border:
        1px solid
        rgba(16,24,40,.06);

    box-shadow:
        0 8px 26px
        rgba(16,24,40,.055);

    backdrop-filter:
        blur(16px);
}

.profile-mini-avatar {
    width: 40px;
    height: 40px;

    border-radius: 13px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #34c759,
            #007aff
        );

    color: white;

    font-size: 14px;
    font-weight: 750;
}

.profile-card-content {
    text-align: left;
}

.profile-name {
    font-size: 15px;
    line-height: 1.2;

    font-weight: 720;

    color: #101828;
}

.profile-role {
    margin-top: 2px;

    font-size: 12px;

    color: #667085;
}

.profile-brands {
    margin-top: 2px;

    font-size: 11px;
    font-weight: 650;

    color: #16864c;

    letter-spacing: .25px;
}


/* ========================================================
   SEZIONI
   ======================================================== */

.section-header {
    display: flex;
    align-items: center;

    gap: 11px;

    margin-top: 29px;
    margin-bottom: 13px;
}

.section-number {
    min-width: 31px;
    width: 31px;
    height: 31px;

    border-radius: 10px;

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

    font-size: 13px;
    font-weight: 750;

    box-shadow:
        0 6px 15px
        rgba(52,199,89,.17);
}

.section-title {
    font-size: 18px;

    font-weight: 720;

    letter-spacing: -.25px;

    color: #101828;

    margin: 0;
}

.section-subtitle {
    margin-top: 1px;

    font-size: 12px;

    color: #98a2b3;
}


/* ========================================================
   LABEL
   ======================================================== */

label[data-testid="stWidgetLabel"] p {
    font-size: 13px !important;

    font-weight: 600 !important;

    color: #475467 !important;
}


/* ========================================================
   INPUT / SELECT
   ======================================================== */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,.96)
        !important;

    border:
        1px solid
        #e4e7ec
        !important;

    border-radius:
        14px
        !important;

    min-height: 48px;

    box-shadow:
        0 2px 7px
        rgba(16,24,40,.025);

    transition:
        border-color .18s ease,
        box-shadow .18s ease;
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


/* ========================================================
   DATE INPUT
   ======================================================== */

div[data-testid="stDateInput"] input {

    background:
        rgba(255,255,255,.96)
        !important;

    border-radius:
        14px
        !important;
}


/* ========================================================
   DISPONIBILITÀ
   ======================================================== */

.availability-card {

    display: flex;
    align-items: center;

    margin-top: 4px;
    margin-bottom: 14px;

    padding:
        12px 14px;

    border-radius:
        14px;

    background:
        rgba(52,199,89,.075);

    border:
        1px solid
        rgba(52,199,89,.15);

    color:
        #18743e;

    font-size:
        13px;

    font-weight:
        620;
}


/* ========================================================
   ALERT STREAMLIT
   ======================================================== */

div[data-testid="stAlert"] {

    border-radius:
        14px;

    border:
        1px solid
        rgba(16,24,40,.05);
}


/* ========================================================
   BUTTON
   ======================================================== */

div[data-testid="stButton"] button {

    min-height:
        50px;

    border-radius:
        14px
        !important;

    font-size:
        15px
        !important;

    font-weight:
        680
        !important;

    transition:
        transform .12s ease,
        box-shadow .15s ease;
}

div[data-testid="stButton"] button:hover {

    transform:
        translateY(-1px);
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
        rgba(32,148,71,.20)
        !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {

    box-shadow:
        0 13px 28px
        rgba(32,148,71,.25)
        !important;
}


/* ========================================================
   SUCCESS
   ======================================================== */

.success-card {

    margin-top:
        18px;

    padding:
        26px;

    border-radius:
        24px;

    background:
        rgba(255,255,255,.90);

    border:
        1px solid
        rgba(52,199,89,.16);

    box-shadow:
        0 18px 45px
        rgba(16,24,40,.07);

    backdrop-filter:
        blur(18px);
}

.success-icon {

    width:
        54px;

    height:
        54px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border-radius:
        18px;

    background:
        linear-gradient(
            135deg,
            #34c759,
            #1e9b4a
        );

    color:
        white;

    font-size:
        27px;

    font-weight:
        700;

    margin-bottom:
        17px;

    box-shadow:
        0 9px 22px
        rgba(52,199,89,.20);
}

.success-title {

    font-size:
        25px;

    font-weight:
        750;

    letter-spacing:
        -.6px;

    color:
        #101828;

    margin-bottom:
        7px;
}

.success-text {

    color:
        #667085;

    font-size:
        14px;

    line-height:
        1.55;

    margin-bottom:
        18px;
}

.success-details {

    padding:
        16px;

    border-radius:
        15px;

    background:
        #f8faf9;

    border:
        1px solid
        #edf1ee;

    color:
        #344054;

    font-size:
        14px;

    line-height:
        1.9;
}


/* ========================================================
   FOOTER
   ======================================================== */

.footer-note {

    text-align:
        center;

    max-width:
        440px;

    margin:
        30px auto 0 auto;

    color:
        #98a2b3;

    font-size:
        11px;

    line-height:
        1.5;
}


/* ========================================================
   MOBILE
   ======================================================== */

@media (max-width: 640px) {

    .block-container {

        padding-top:
            1rem;

        padding-left:
            1rem;

        padding-right:
            1rem;

        padding-bottom:
            2.5rem;
    }

    .profile-header {

        margin-bottom:
            1.55rem;
    }

    .profile-monogram {

        width:
            60px;

        height:
            60px;

        border-radius:
            19px;

        font-size:
            21px;

        margin-bottom:
            14px;
    }

    .booking-title {

        font-size:
            28px;

        letter-spacing:
            -.9px;
    }

    .profile-description {

        font-size:
            14px;

        padding:
            0 8px;
    }

    .profile-card {

        margin-top:
            17px;
    }

    .section-header {

        margin-top:
            24px;

        margin-bottom:
            11px;
    }

    .section-title {

        font-size:
            17px;
    }

    .success-card {

        padding:
            21px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)# =========================================================
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
                # NOTIFICA PUSH PUSHOVER
                # =========================================
                #
                # La prenotazione è già stata registrata
                # su Google Calendar.
                #
                # Un eventuale problema di Pushover
                # NON deve far fallire la prenotazione.
                # =========================================

                try:

                    send_booking_notification(

                        nome_farmacia=
                            nome_farmacia.strip(),

                        cap=
                            cap.strip(),

                        start_datetime=
                            selected_slot["start"],

                        durata=
                            durata,

                        referente=
                            referente.strip(),
                    )

                except Exception:
                    pass

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
