from datetime import date
import html

import streamlit as st

from booking import get_available_slots, format_slot
from google_calendar import create_appointment


# =========================================================
# CONFIGURAZIONE PAGINA
# =========================================================

st.set_page_config(
    page_title="Prenota una visita",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

if "slot_verificato" not in st.session_state:
    st.session_state.slot_verificato = None

if "prenotazione_completata" not in st.session_state:
    st.session_state.prenotazione_completata = False


# =========================================================
# DESIGN
# =========================================================

st.markdown(
    """
<style>

/* =========================================
   PAGINA
========================================= */

html,
body,
.stApp {
    background: #f5f5f7 !important;
}

.block-container {
    max-width: 560px !important;
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
}


/* =========================================
   NASCONDE ELEMENTI STREAMLIT
========================================= */

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


/* =========================================
   FONT
========================================= */

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


/* =========================================
   HERO
========================================= */

.booking-hero {
    text-align: center;
    padding-top: 8px;
    margin-bottom: 36px;
}

.booking-icon {
    width: 58px;
    height: 58px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 20px auto;

    border-radius: 17px;

    background: #1d1d1f;
    color: #ffffff;

    font-size: 27px;
    font-weight: 600;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.12);
}

.booking-title {
    color: #1d1d1f;

    font-size: 36px;
    line-height: 1.08;

    font-weight: 700;

    letter-spacing: -1.2px;
}

.booking-subtitle {
    color: #6e6e73;

    font-size: 17px;
    line-height: 1.45;

    margin-top: 10px;
}


/* =========================================
   TITOLI SEZIONI
========================================= */

h3 {
    color: #1d1d1f !important;

    font-size: 19px !important;
    line-height: 1.3 !important;

    font-weight: 650 !important;

    letter-spacing: -0.3px !important;

    margin-top: 34px !important;
    margin-bottom: 10px !important;
}


/* =========================================
   LABEL
========================================= */

div[data-testid="stWidgetLabel"] p {
    color: #3a3a3c !important;

    font-size: 14px !important;
    font-weight: 500 !important;

    margin-bottom: 5px !important;
}


/* =========================================
   INPUT
========================================= */

div[data-baseweb="input"] {
    background: #ffffff !important;

    border: 1px solid #d2d2d7 !important;
    border-radius: 14px !important;

    min-height: 52px !important;

    box-shadow: none !important;
}

div[data-baseweb="input"] > div {
    background: #ffffff !important;
}

div[data-baseweb="input"] input {
    background: #ffffff !important;

    color: #1d1d1f !important;

    font-size: 16px !important;

    min-height: 50px !important;

    -webkit-text-fill-color: #1d1d1f !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #86868b !important;
    -webkit-text-fill-color: #86868b !important;
    opacity: 1 !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: #0071e3 !important;

    box-shadow:
        0 0 0 3px rgba(0, 113, 227, 0.12)
        !important;
}


/* =========================================
   SELECT
========================================= */

div[data-baseweb="select"] > div {
    background: #ffffff !important;

    border: 1px solid #d2d2d7 !important;
    border-radius: 14px !important;

    min-height: 52px !important;

    box-shadow: none !important;

    color: #1d1d1f !important;
}

div[data-baseweb="select"] span {
    color: #1d1d1f !important;
}

div[data-baseweb="select"] svg {
    fill: #6e6e73 !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: #0071e3 !important;

    box-shadow:
        0 0 0 3px rgba(0, 113, 227, 0.12)
        !important;
}


/* =========================================
   DATA
========================================= */

div[data-testid="stDateInput"] input {
    background: #ffffff !important;

    color: #1d1d1f !important;

    -webkit-text-fill-color: #1d1d1f !important;

    font-size: 16px !important;
}


/* =========================================
   TESTI SECONDARI
========================================= */

div[data-testid="stCaptionContainer"] p {
    color: #86868b !important;
    font-size: 13px !important;
}


/* =========================================
   PULSANTI
========================================= */

div[data-testid="stButton"] {
    margin-top: 18px;
}

div[data-testid="stButton"] button {
    width: 100% !important;

    min-height: 54px !important;

    border-radius: 14px !important;

    font-size: 16px !important;
    font-weight: 600 !important;

    border: none !important;

    transition:
        transform 0.12s ease,
        opacity 0.12s ease,
        background 0.12s ease;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #1d1d1f !important;
    color: #ffffff !important;
}

div[data-testid="stButton"] button[kind="primary"] p {
    color: #ffffff !important;
}

div[data-testid="stButton"] button[kind="secondary"] {
    background: #1d1d1f !important;
    color: #ffffff !important;
}

div[data-testid="stButton"] button[kind="secondary"] p {
    color: #ffffff !important;
}

div[data-testid="stButton"] button:hover {
    background: #000000 !important;
}

div[data-testid="stButton"] button:active {
    transform: scale(0.985);
}

div[data-testid="stButton"] button:disabled {
    background: #d2d2d7 !important;
    color: #86868b !important;
    opacity: 1 !important;
}


/* =========================================
   ALERT
========================================= */

div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: none !important;
}


/* =========================================
   CARD DISPONIBILITÀ
========================================= */

.appointment-card {
    background: #ffffff;

    border: 1px solid rgba(0, 0, 0, 0.07);

    border-radius: 22px;

    padding: 24px;

    margin-top: 26px;
    margin-bottom: 6px;

    box-shadow:
        0 10px 35px rgba(0, 0, 0, 0.06);
}

.available-badge {
    display: inline-flex;

    align-items: center;
    justify-content: center;

    background: #e8f7ed;
    color: #147a35;

    border-radius: 100px;

    padding: 7px 12px;

    font-size: 13px;
    font-weight: 650;

    margin-bottom: 18px;
}

.appointment-date {
    color: #6e6e73;

    font-size: 15px;
    font-weight: 500;

    margin-bottom: 3px;
}

.appointment-time {
    color: #1d1d1f;

    font-size: 31px;
    line-height: 1.15;

    font-weight: 700;

    letter-spacing: -0.8px;

    margin-bottom: 18px;
}

.appointment-pharmacy {
    color: #1d1d1f;

    font-size: 16px;
    font-weight: 600;

    margin-bottom: 4px;
}

.appointment-details {
    color: #6e6e73;

    font-size: 14px;
    line-height: 1.5;
}


/* =========================================
   SUCCESS CARD
========================================= */

.success-card {
    text-align: center;

    background: #ffffff;

    border: 1px solid rgba(0, 0, 0, 0.07);

    border-radius: 24px;

    padding: 32px 22px;

    margin-top: 28px;

    box-shadow:
        0 12px 40px rgba(0, 0, 0, 0.06);
}

.success-icon {
    width: 58px;
    height: 58px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 18px auto;

    border-radius: 50%;

    background: #e8f7ed;
    color: #147a35;

    font-size: 28px;
    font-weight: 700;
}

.success-title {
    color: #1d1d1f;

    font-size: 24px;
    font-weight: 700;

    letter-spacing: -0.5px;
}

.success-text {
    color: #6e6e73;

    font-size: 15px;
    line-height: 1.6;

    margin-top: 10px;
}


/* =========================================
   MOBILE
========================================= */

@media (max-width: 640px) {

    .block-container {
        padding-top: 1.25rem !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }

    .booking-hero {
        margin-bottom: 28px;
    }

    .booking-icon {
        width: 54px;
        height: 54px;
        border-radius: 16px;
    }

    .booking-title {
        font-size: 30px;
    }

    .booking-subtitle {
        font-size: 16px;
    }

    .appointment-card {
        padding: 21px;
    }

    .appointment-time {
        font-size: 28px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HERO
# IMPORTANTE: HTML SENZA INDENTAZIONE
# =========================================================

st.markdown(
    """
<div class="booking-hero">
<div class="booking-icon">◉</div>
<div class="booking-title">Prenota una visita</div>
<div class="booking-subtitle">Scegli il momento più comodo per incontrarci.</div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# FARMACIA
# =========================================================

st.subheader("Farmacia")

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
# APPUNTAMENTO
# =========================================================

st.subheader("Appuntamento")

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
    "Durata",
    options=list(durate.keys()),
    index=3,
)

durata = durate[durata_label]


oggi = date.today()

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

    except Exception:

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
        "Orario",
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
        "Nessun orario disponibile per "
        "questa data e questa durata."
    )


# =========================================================
# CONTATTI
# =========================================================

st.subheader("Contatti")

st.caption(
    "Facoltativi — utili in caso di necessità."
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
# FIRMA DATI
# Se cambia qualcosa dopo la verifica,
# la disponibilità viene invalidata.
# =========================================================

firma_corrente = None

if slot_selezionato:

    firma_corrente = (
        nome_farmacia.strip(),
        cap.strip(),
        durata,
        slot_selezionato["start"],
        slot_selezionato["end"],
    )


if (
    st.session_state.slot_verificato
    and
    st.session_state.slot_verificato.get("firma")
    != firma_corrente
):

    st.session_state.slot_verificato = None


# =========================================================
# VERIFICA DISPONIBILITÀ
# =========================================================

verifica = st.button(
    "Verifica disponibilità",
    type="primary",
    use_container_width=True,
    disabled=slot_selezionato is None,
)


if verifica:

    nome_pulito = nome_farmacia.strip()
    cap_pulito = cap.strip()

    errori = []

    if not nome_pulito:

        errori.append(
            "Inserisci il nome della farmacia."
        )

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


    if errori:

        st.session_state.slot_verificato = None

        for errore in errori:
            st.error(errore)

    else:

        try:

            # Ricontrollo Google Calendar
            # al momento della verifica

            slots_aggiornati = get_available_slots(
                data_appuntamento,
                durata,
            )

            ancora_disponibile = any(
                slot["start"]
                == slot_selezionato["start"]
                and
                slot["end"]
                == slot_selezionato["end"]
                for slot in slots_aggiornati
            )


            if ancora_disponibile:

                st.session_state.slot_verificato = {
                    "start":
                        slot_selezionato["start"],

                    "end":
                        slot_selezionato["end"],

                    "firma":
                        firma_corrente,
                }

            else:

                st.session_state.slot_verificato = None

                st.warning(
                    "Questa fascia non è più "
                    "disponibile. Scegli un altro "
                    "orario."
                )

                st.rerun()


        except Exception:

            st.session_state.slot_verificato = None

            st.error(
                "Non è stato possibile verificare "
                "la disponibilità."
            )


# =========================================================
# CARD DOPO VERIFICA
# =========================================================

if st.session_state.slot_verificato:

    slot_salvato = (
        st.session_state.slot_verificato
    )

    data_testo = (
        data_appuntamento.strftime(
            "%d/%m/%Y"
        )
    )

    orario_testo = (
        f"{slot_salvato['start'].strftime('%H:%M')}"
        f" – "
        f"{slot_salvato['end'].strftime('%H:%M')}"
    )

    # Evita che testo inserito dall'utente
    # venga interpretato come HTML.

    farmacia_html = html.escape(
        nome_farmacia.strip()
    )

    cap_html = html.escape(
        cap.strip()
    )


    st.markdown(
        f"""
<div class="appointment-card">
<div class="available-badge">✓ Disponibile</div>
<div class="appointment-date">{data_testo}</div>
<div class="appointment-time">{orario_testo}</div>
<div class="appointment-pharmacy">{farmacia_html}</div>
<div class="appointment-details">
CAP {cap_html}<br>
Durata {durata} minuti
</div>
</div>
""",
        unsafe_allow_html=True,
    )


    # =====================================================
    # PRENOTAZIONE
    # =====================================================

    prenota = st.button(
        "Prenota appuntamento",
        type="primary",
        use_container_width=True,
    )


    if prenota:

        try:

            # Ultimo controllo immediatamente
            # prima della scrittura su Calendar.

            slots_finali = get_available_slots(
                data_appuntamento,
                durata,
            )

            ancora_libero = any(
                slot["start"]
                == slot_salvato["start"]
                and
                slot["end"]
                == slot_salvato["end"]
                for slot in slots_finali
            )


            if not ancora_libero:

                st.session_state.slot_verificato = None

                st.error(
                    "Questo orario è stato appena "
                    "occupato. Scegli un altro orario."
                )

                st.rerun()


            else:

                create_appointment(
                    nome_farmacia=
                        nome_farmacia.strip(),

                    cap=
                        cap.strip(),

                    start_datetime=
                        slot_salvato["start"],

                    end_datetime=
                        slot_salvato["end"],

                    durata=
                        durata,

                    referente=
                        referente.strip(),

                    telefono=
                        telefono.strip(),

                    email=
                        email.strip(),
                )


                st.session_state.slot_verificato = None

                st.session_state.prenotazione_completata = True


                farmacia_success = html.escape(
                    nome_farmacia.strip()
                )


                st.markdown(
                    f"""
<div class="success-card">
<div class="success-icon">✓</div>
<div class="success-title">Appuntamento confermato</div>
<div class="success-text">
{data_testo}<br>
<strong>{orario_testo}</strong><br><br>
{farmacia_success}
</div>
</div>
""",
                    unsafe_allow_html=True,
                )


        except Exception:

            st.error(
                "Non è stato possibile registrare "
                "l'appuntamento. Riprova."
            )
