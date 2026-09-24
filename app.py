from datetime import datetime
from zoneinfo import ZoneInfo
import html

import streamlit as st

from booking import get_available_slots, format_slot
from google_calendar import create_appointment


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
# DESIGN
# =========================================================

st.markdown(
    """
<style>

/* ======================================================
   PAGINA
====================================================== */

html,
body,
.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(52, 199, 89, 0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 95% 12%,
            rgba(0, 122, 255, 0.08),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #f8faf9 0%,
            #f5f7f8 50%,
            #f8f9fa 100%
        ) !important;
}

.block-container {
    max-width: 590px !important;

    padding-top: 2rem !important;
    padding-bottom: 5rem !important;

    padding-left: 20px !important;
    padding-right: 20px !important;
}


/* ======================================================
   NASCONDE ELEMENTI STREAMLIT
====================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
}


/* ======================================================
   FONT
====================================================== */

html,
body,
[class*="css"],
.stApp {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "SF Pro Display",
        "SF Pro Text",
        "Helvetica Neue",
        Arial,
        sans-serif !important;
}


/* ======================================================
   HERO
====================================================== */

.booking-hero {
    text-align: center;

    padding-top: 8px;

    margin-bottom: 32px;
}


.profile-monogram {
    width: 68px;
    height: 68px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 20px auto;

    border-radius: 21px;

    background:
        linear-gradient(
            135deg,
            #34c759 0%,
            #168f69 55%,
            #087ca7 100%
        );

    color: #ffffff;

    font-size: 21px;
    font-weight: 750;

    letter-spacing: -0.5px;

    box-shadow:
        0 12px 30px rgba(30, 150, 90, 0.22);
}


.booking-title {
    color: #161617;

    font-size: 38px;
    line-height: 1.07;

    font-weight: 750;

    letter-spacing: -1.4px;
}


.profile-name {
    margin-top: 21px;

    color: #1d1d1f;

    font-size: 21px;

    font-weight: 680;

    letter-spacing: -0.35px;
}


.profile-role {
    margin-top: 3px;

    color: #6e6e73;

    font-size: 15px;

    font-weight: 500;
}


.profile-brands {
    display: inline-block;

    margin-top: 13px;

    padding: 8px 15px;

    background:
        rgba(255, 255, 255, 0.86);

    border:
        1px solid rgba(0, 0, 0, 0.07);

    border-radius: 100px;

    color: #3a3a3c;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: 0.4px;

    box-shadow:
        0 4px 14px rgba(0, 0, 0, 0.04);
}


.booking-subtitle {
    max-width: 430px;

    margin: 18px auto 0 auto;

    color: #6e6e73;

    font-size: 16px;

    line-height: 1.55;
}


/* ======================================================
   SEZIONI
====================================================== */

.section-header {
    display: flex;

    align-items: center;

    gap: 10px;

    margin-top: 30px;
    margin-bottom: 13px;
}


.section-number {
    width: 28px;
    height: 28px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 9px;

    background:
        linear-gradient(
            135deg,
            rgba(52, 199, 89, 0.15),
            rgba(0, 122, 255, 0.10)
        );

    color: #168548;

    font-size: 13px;

    font-weight: 750;
}


.section-title {
    color: #1d1d1f;

    font-size: 19px;

    font-weight: 680;

    letter-spacing: -0.35px;
}


.section-subtitle {
    color: #86868b;

    font-size: 13px;

    margin-top: -5px;
    margin-bottom: 14px;
}


/* ======================================================
   LABEL
====================================================== */

div[data-testid="stWidgetLabel"] p {
    color: #3a3a3c !important;

    font-size: 14px !important;

    font-weight: 550 !important;
}


/* ======================================================
   INPUT
====================================================== */

div[data-baseweb="input"] {
    background: #ffffff !important;

    border:
        1px solid rgba(0, 0, 0, 0.12) !important;

    border-radius: 14px !important;

    min-height: 52px !important;

    box-shadow:
        0 3px 10px rgba(0, 0, 0, 0.025) !important;
}


div[data-baseweb="input"] > div {
    background: #ffffff !important;
}


div[data-baseweb="input"] input {
    background: #ffffff !important;

    color: #1d1d1f !important;

    -webkit-text-fill-color:
        #1d1d1f !important;

    font-size: 16px !important;

    min-height: 50px !important;
}


div[data-baseweb="input"] input::placeholder {
    color: #a1a1a6 !important;

    -webkit-text-fill-color:
        #a1a1a6 !important;

    opacity: 1 !important;
}


div[data-baseweb="input"]:focus-within {
    border-color:
        #27a956 !important;

    box-shadow:
        0 0 0 3px rgba(39, 169, 86, 0.12)
        !important;
}


/* ======================================================
   SELECT
====================================================== */

div[data-baseweb="select"] > div {
    background: #ffffff !important;

    border:
        1px solid rgba(0, 0, 0, 0.12) !important;

    border-radius: 14px !important;

    min-height: 52px !important;

    box-shadow:
        0 3px 10px rgba(0, 0, 0, 0.025) !important;

    color: #1d1d1f !important;
}


div[data-baseweb="select"] span {
    color: #1d1d1f !important;
}


div[data-baseweb="select"] svg {
    fill: #6e6e73 !important;
}


div[data-baseweb="select"] > div:focus-within {
    border-color:
        #27a956 !important;

    box-shadow:
        0 0 0 3px rgba(39, 169, 86, 0.12)
        !important;
}


/* ======================================================
   DATA
====================================================== */

div[data-testid="stDateInput"] input {
    background: #ffffff !important;

    color: #1d1d1f !important;

    -webkit-text-fill-color:
        #1d1d1f !important;

    font-size: 16px !important;
}


/* ======================================================
   CAPTION
====================================================== */

div[data-testid="stCaptionContainer"] p {
    color: #86868b !important;

    font-size: 13px !important;
}


/* ======================================================
   PULSANTE PRENOTA - VERDE
====================================================== */

div[data-testid="stButton"] {
    margin-top: 24px;
}


div[data-testid="stButton"] button {
    width: 100% !important;

    min-height: 58px !important;

    border-radius: 16px !important;

    font-size: 16px !important;

    font-weight: 680 !important;

    border: none !important;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease;
}


div[data-testid="stButton"] button[kind="primary"] {
    background:
        linear-gradient(
            135deg,
            #34c759 0%,
            #209447 100%
        ) !important;

    color: #ffffff !important;

    box-shadow:
        0 10px 24px rgba(32, 148, 71, 0.24)
        !important;
}


div[data-testid="stButton"] button[kind="primary"] p {
    color: #ffffff !important;
}


div[data-testid="stButton"] button[kind="primary"]:hover {
    background:
        linear-gradient(
            135deg,
            #2eb653 0%,
            #197d3b 100%
        ) !important;

    box-shadow:
        0 12px 28px rgba(32, 148, 71, 0.30)
        !important;

    transform: translateY(-1px);
}


div[data-testid="stButton"] button[kind="primary"]:active {
    transform: scale(0.985);
}


div[data-testid="stButton"] button:disabled {
    background: #d7d7da !important;

    color: #8e8e93 !important;

    box-shadow: none !important;

    opacity: 1 !important;
}


/* ======================================================
   PULSANTE SECONDARIO
====================================================== */

div[data-testid="stButton"] button[kind="secondary"] {
    background: #ffffff !important;

    color: #1d1d1f !important;

    border:
        1px solid rgba(0, 0, 0, 0.10) !important;

    box-shadow:
        0 4px 14px rgba(0, 0, 0, 0.04)
        !important;
}


div[data-testid="stButton"] button[kind="secondary"] p {
    color: #1d1d1f !important;
}


/* ======================================================
   ALERT
====================================================== */

div[data-testid="stAlert"] {
    border-radius: 15px !important;

    border: none !important;
}


/* ======================================================
   DISPONIBILITÀ
====================================================== */

.availability-card {
    display: flex;

    align-items: center;

    gap: 11px;

    background:
        linear-gradient(
            135deg,
            rgba(232, 248, 237, 0.95),
            rgba(242, 250, 246, 0.95)
        );

    border:
        1px solid rgba(52, 199, 89, 0.18);

    border-radius: 15px;

    padding: 14px 15px;

    margin-top: 14px;
}


.availability-icon {
    width: 30px;
    height: 30px;

    min-width: 30px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: #34c759;

    color: white;

    font-size: 14px;

    font-weight: 750;
}


.availability-text {
    color: #315d3d;

    font-size: 13px;

    line-height: 1.4;
}


.availability-text strong {
    color: #176b35;
}


/* ======================================================
   DIVISORE
====================================================== */

.soft-divider {
    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(0,0,0,0.08),
            transparent
        );

    margin-top: 32px;
}


/* ======================================================
   PRIVACY / INFO
====================================================== */

.booking-info {
    text-align: center;

    color: #86868b;

    font-size: 12px;

    line-height: 1.5;

    margin-top: 15px;

    padding: 0 10px;
}


/* ======================================================
   SUCCESS
====================================================== */

.success-card {
    text-align: center;

    background:
        rgba(255,255,255,0.94);

    border:
        1px solid rgba(0,0,0,0.06);

    border-radius: 28px;

    padding: 38px 25px;

    margin-top: 20px;

    box-shadow:
        0 18px 55px rgba(0,0,0,0.08);
}


.success-icon {
    width: 68px;
    height: 68px;

    display: flex;

    align-items: center;
    justify-content: center;

    margin: 0 auto 21px auto;

    border-radius: 50%;

    background:
        linear-gradient(
            135deg,
            #34c759,
            #209447
        );

    color: #ffffff;

    font-size: 31px;

    font-weight: 750;

    box-shadow:
        0 10px 25px rgba(32,148,71,0.22);
}


.success-title {
    color: #1d1d1f;

    font-size: 26px;

    font-weight: 750;

    letter-spacing: -0.7px;
}


.success-with {
    color: #86868b;

    font-size: 12px;

    margin-top: 24px;

    text-transform: uppercase;

    letter-spacing: 0.8px;
}


.success-name {
    color: #1d1d1f;

    font-size: 21px;

    font-weight: 680;

    margin-top: 5px;
}


.success-role {
    color: #6e6e73;

    font-size: 14px;

    margin-top: 3px;
}


.success-brands {
    display: inline-block;

    color: #315d3d;

    background: #edf8f0;

    border-radius: 100px;

    padding: 6px 12px;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 0.35px;

    margin-top: 10px;
}


.success-divider {
    height: 1px;

    background: #e5e5e7;

    margin: 27px 0;
}


.success-pharmacy {
    color: #1d1d1f;

    font-size: 18px;

    font-weight: 650;
}


.success-date {
    color: #6e6e73;

    font-size: 15px;

    margin-top: 18px;
}


.success-time {
    color: #1d1d1f;

    font-size: 30px;

    font-weight: 750;

    letter-spacing: -0.7px;

    margin-top: 4px;
}


.success-details {
    color: #6e6e73;

    font-size: 14px;

    line-height: 1.6;

    margin-top: 9px;
}


/* ======================================================
   MOBILE
====================================================== */

@media (max-width: 640px) {

    .block-container {
        padding-top: 1.2rem !important;

        padding-left: 16px !important;

        padding-right: 16px !important;
    }


    .booking-hero {
        margin-bottom: 27px;
    }


    .profile-monogram {
        width: 62px;
        height: 62px;

        border-radius: 19px;
    }


    .booking-title {
        font-size: 31px;
    }


    .profile-name {
        font-size: 19px;

        margin-top: 18px;
    }


    .booking-subtitle {
        font-size: 15px;
    }


    .section-header {
        margin-top: 27px;
    }


    .success-card {
        padding: 31px 20px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SCHERMATA FINALE
# =========================================================

if (
    st.session_state.prenotazione_completata
    and st.session_state.ultima_prenotazione
):

    dati = st.session_state.ultima_prenotazione

    farmacia_html = html.escape(
        dati["farmacia"]
    )

    cap_html = html.escape(
        dati["cap"]
    )


    st.markdown(
        f"""
<div class="booking-hero">

<div class="profile-monogram">
AI
</div>

<div class="booking-title">
Prenotazione completata
</div>

<div class="booking-subtitle">
La visita è stata registrata correttamente.
</div>

</div>


<div class="success-card">

<div class="success-icon">
✓
</div>

<div class="success-title">
Appuntamento confermato
</div>


<div class="success-with">
Appuntamento con
</div>

<div class="success-name">
Alessandro Iovine
</div>

<div class="success-role">
Sales Manager
</div>

<div class="success-brands">
PIC · CONTROL · EFFERDENT
</div>


<div class="success-divider">
</div>


<div class="success-pharmacy">
{farmacia_html}
</div>

<div class="success-date">
{dati["data"]}
</div>

<div class="success-time">
{dati["orario"]}
</div>

<div class="success-details">
Durata {dati["durata"]} minuti<br>
CAP {cap_html}
</div>

</div>
""",
        unsafe_allow_html=True,
    )


    if st.button(
        "Prenota un altro appuntamento",
        use_container_width=True,
    ):

        st.session_state.prenotazione_completata = False

        st.session_state.ultima_prenotazione = None

        st.rerun()


    st.stop()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
<div class="booking-hero">

<div class="profile-monogram">
AI
</div>

<div class="booking-title">
Prenota un appuntamento
</div>

<div class="profile-name">
Alessandro Iovine
</div>

<div class="profile-role">
Sales Manager
</div>

<div class="profile-brands">
PIC&nbsp;&nbsp;·&nbsp;&nbsp;CONTROL&nbsp;&nbsp;·&nbsp;&nbsp;EFFERDENT
</div>

<div class="booking-subtitle">
Scegli giorno e orario per fissare
un appuntamento presso la tua farmacia.
</div>

</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SEZIONE 1 - FARMACIA
# =========================================================

st.markdown(
    """
<div class="section-header">
<div class="section-number">1</div>
<div class="section-title">La tua farmacia</div>
</div>
""",
    unsafe_allow_html=True,
)


nome_farmacia = st.text_input(
    "Nome farmacia",
    placeholder="Farmacia Centrale",
)


cap = st.text_input(
    "CAP",
    max_chars=5,
    placeholder="80100",
)


st.caption(
    "Nome farmacia e CAP sono obbligatori."
)


# =========================================================
# DIVISORE
# =========================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# SEZIONE 2 - APPUNTAMENTO
# =========================================================

st.markdown(
    """
<div class="section-header">
<div class="section-number">2</div>
<div class="section-title">Quando preferisci incontrarci?</div>
</div>

<div class="section-subtitle">
Scegli durata, giorno e orario della visita.
</div>
""",
    unsafe_allow_html=True,
)


durate = {
    "30 minuti": 30,
    "45 minuti": 45,
    "60 minuti": 60,
    "75 minuti": 75,
    "90 minuti": 90,
    "105 minuti": 105,
    "120 minuti": 120,
}


durata_label = st.selectbox(
    "Durata della visita",
    options=list(durate.keys()),
    index=3,
)


durata = durate[
    durata_label
]


oggi = datetime.now(
    TIMEZONE
).date()


data_appuntamento = st.date_input(
    "Data",
    value=oggi,
    min_value=oggi,
    format="DD/MM/YYYY",
)


# =========================================================
# DISPONIBILITÀ
# =========================================================

giorno_valido = (
    data_appuntamento.weekday() < 5
)


slots = []


if not giorno_valido:

    st.warning(
        "Le visite sono disponibili "
        "dal lunedì al venerdì."
    )


else:

    try:

        slots = get_available_slots(
            data_appuntamento,
            durata,
        )


        # ---------------------------------------------
        # NASCONDE ORARI GIÀ TRASCORSI
        # ---------------------------------------------

        if data_appuntamento == oggi:

            adesso = datetime.now(
                TIMEZONE
            )

            slots = [
                slot
                for slot in slots
                if slot["start"] > adesso
            ]


    except Exception:

        slots = []

        st.error(
            "Non è stato possibile verificare "
            "le disponibilità."
        )


# =========================================================
# ORARIO
# =========================================================

slot_selezionato = None


if giorno_valido and slots:

    slot_selezionato = st.selectbox(
        "Orario disponibile",
        options=slots,
        format_func=format_slot,
    )


    if len(slots) == 1:

        st.caption(
            "1 orario disponibile"
        )

    else:

        st.caption(
            f"{len(slots)} orari disponibili"
        )


elif giorno_valido:

    st.info(
        "Non ci sono orari disponibili "
        "per questa data e questa durata."
    )


# =========================================================
# DISPONIBILITÀ VISIVA
# =========================================================

if slot_selezionato:

    st.markdown(
        """
<div class="availability-card">

<div class="availability-icon">
✓
</div>

<div class="availability-text">
<strong>Orario disponibile</strong><br>
La disponibilità verrà ricontrollata
automaticamente prima della conferma.
</div>

</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# DIVISORE
# =========================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# SEZIONE 3 - CONTATTI
# =========================================================

st.markdown(
    """
<div class="section-header">
<div class="section-number">3</div>
<div class="section-title">I tuoi contatti</div>
</div>

<div class="section-subtitle">
Facoltativi — utili in caso di necessità.
</div>
""",
    unsafe_allow_html=True,
)


referente = st.text_input(
    "Referente",
    placeholder="Nome e cognome",
)


telefono = st.text_input(
    "Telefono",
    placeholder="333 1234567",
)


email = st.text_input(
    "Email",
    placeholder="nome@farmacia.it",
)


# =========================================================
# PULSANTE PRENOTAZIONE
# =========================================================

prenota = st.button(
    "Prenota appuntamento",
    type="primary",
    use_container_width=True,
    disabled=slot_selezionato is None,
)


st.markdown(
    """
<div class="booking-info">
La prenotazione verrà registrata direttamente
nel calendario di Alessandro Iovine.
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# PRENOTAZIONE
# =========================================================

if prenota:

    nome_pulito = (
        nome_farmacia.strip()
    )

    cap_pulito = (
        cap.strip()
    )

    errori = []


    # -----------------------------------------------------
    # VALIDAZIONE NOME
    # -----------------------------------------------------

    if not nome_pulito:

        errori.append(
            "Inserisci il nome della farmacia."
        )


    # -----------------------------------------------------
    # VALIDAZIONE CAP
    # -----------------------------------------------------

    if not cap_pulito:

        errori.append(
            "Inserisci il CAP."
        )

    elif (
        not cap_pulito.isdigit()
        or len(cap_pulito) != 5
    ):

        errori.append(
            "Inserisci un CAP valido di 5 cifre."
        )


    # -----------------------------------------------------
    # ERRORI
    # -----------------------------------------------------

    if errori:

        for errore in errori:

            st.error(
                errore
            )


    else:

        try:

            # =============================================
            # RICONTROLLO GOOGLE CALENDAR
            # =============================================

            slots_finali = get_available_slots(
                data_appuntamento,
                durata,
            )


            # ---------------------------------------------
            # ESCLUDE ORARI TRASCORSI
            # ---------------------------------------------

            if data_appuntamento == oggi:

                adesso = datetime.now(
                    TIMEZONE
                )

                slots_finali = [
                    slot
                    for slot in slots_finali
                    if slot["start"] > adesso
                ]


            # ---------------------------------------------
            # VERIFICA SLOT
            # ---------------------------------------------

            ancora_libero = any(

                slot["start"]
                == slot_selezionato["start"]

                and

                slot["end"]
                == slot_selezionato["end"]

                for slot
                in slots_finali
            )


            # ---------------------------------------------
            # NON PIÙ DISPONIBILE
            # ---------------------------------------------

            if not ancora_libero:

                st.error(
                    "Questo orario è stato appena "
                    "occupato. Scegli un altro orario."
                )

                st.rerun()


            # =============================================
            # CREA EVENTO GOOGLE CALENDAR
            # =============================================

            create_appointment(

                nome_farmacia=
                    nome_pulito,

                cap=
                    cap_pulito,

                start_datetime=
                    slot_selezionato["start"],

                end_datetime=
                    slot_selezionato["end"],

                durata=
                    durata,

                referente=
                    referente.strip(),

                telefono=
                    telefono.strip(),

                email=
                    email.strip(),
            )


            # =============================================
            # DATI PER SCHERMATA FINALE
            # =============================================

            st.session_state.ultima_prenotazione = {

                "farmacia":
                    nome_pulito,

                "cap":
                    cap_pulito,

                "data":
                    data_appuntamento.strftime(
                        "%d/%m/%Y"
                    ),

                "orario":
                    format_slot(
                        slot_selezionato
                    ),

                "durata":
                    durata,
            }


            st.session_state.prenotazione_completata = True


            st.rerun()


        except Exception:

            st.error(
                "Non è stato possibile registrare "
                "l'appuntamento. Riprova."
            )
