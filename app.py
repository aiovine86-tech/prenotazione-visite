from datetime import date

import streamlit as st

from booking import get_available_slots, format_slot
from google_calendar import create_appointment


# =========================================================
# CONFIGURAZIONE
# =========================================================

st.set_page_config(
    page_title="Prenota una visita",
    page_icon="◉",
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

    /* ---------- PAGINA ---------- */

    .stApp {
        background:
            linear-gradient(
                180deg,
                #f5f5f7 0%,
                #ffffff 55%,
                #f5f5f7 100%
            );
    }

    .block-container {
        max-width: 560px;
        padding-top: 2.2rem;
        padding-bottom: 5rem;
        padding-left: 20px;
        padding-right: 20px;
    }


    /* ---------- NASCONDE ELEMENTI STREAMLIT ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0;
    }


    /* ---------- FONT ---------- */

    html,
    body,
    [class*="css"] {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "SF Pro Display",
            "SF Pro Text",
            "Helvetica Neue",
            Arial,
            sans-serif;
    }


    /* ---------- HERO ---------- */

    .booking-hero {
        text-align: center;
        margin-bottom: 34px;
    }

    .booking-icon {
        width: 54px;
        height: 54px;
        margin: 0 auto 18px auto;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 16px;

        background: #111111;
        color: white;

        font-size: 25px;
        font-weight: 500;
    }

    .booking-title {
        color: #1d1d1f;

        font-size: 34px;
        line-height: 1.08;

        font-weight: 700;
        letter-spacing: -1.1px;

        margin: 0;
    }

    .booking-subtitle {
        color: #6e6e73;

        font-size: 17px;
        line-height: 1.45;

        margin-top: 10px;
        margin-bottom: 0;
    }


    /* ---------- TITOLI SEZIONE ---------- */

    h3 {
        color: #1d1d1f !important;

        font-size: 18px !important;
        font-weight: 650 !important;

        letter-spacing: -0.25px !important;

        margin-top: 30px !important;
        margin-bottom: 8px !important;
    }


    /* ---------- LABEL ---------- */

    div[data-testid="stWidgetLabel"] p {
        color: #3a3a3c;

        font-size: 14px !important;
        font-weight: 500 !important;

        margin-bottom: 5px;
    }


    /* ---------- INPUT ---------- */

    div[data-baseweb="input"] {
        border-radius: 13px !important;
        border: 1px solid #d2d2d7 !important;

        background: rgba(255,255,255,0.92) !important;

        min-height: 50px;

        box-shadow: none !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #0071e3 !important;

        box-shadow:
            0 0 0 3px rgba(0,113,227,0.12)
            !important;
    }

    div[data-baseweb="input"] input {
        font-size: 16px !important;
        color: #1d1d1f !important;

        min-height: 48px;
    }


    /* ---------- SELECT ---------- */

    div[data-baseweb="select"] > div {
        border-radius: 13px !important;
        border-color: #d2d2d7 !important;

        background: rgba(255,255,255,0.92) !important;

        min-height: 50px;

        box-shadow: none !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: #0071e3 !important;

        box-shadow:
            0 0 0 3px rgba(0,113,227,0.12)
            !important;
    }


    /* ---------- DATE INPUT ---------- */

    div[data-testid="stDateInput"] input {
        font-size: 16px !important;
    }


    /* ---------- CAPTION ---------- */

    div[data-testid="stCaptionContainer"] p {
        color: #86868b !important;
        font-size: 13px !important;
    }


    /* ---------- PULSANTI ---------- */

    div[data-testid="stButton"] {
        margin-top: 15px;
    }

    div[data-testid="stButton"] button {
        width: 100%;

        min-height: 54px;

        border-radius: 14px;

        font-size: 16px;
        font-weight: 600;

        transition:
            transform 0.12s ease,
            opacity 0.12s ease;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: #1d1d1f !important;
        color: #ffffff !important;

        border: none !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #000000 !important;
    }

    div[data-testid="stButton"] button:not([kind="primary"]) {
        background: #1d1d1f;
        color: white;

        border: none;
    }

    div[data-testid="stButton"] button:active {
        transform: scale(0.985);
    }


    /* ---------- ALERT ---------- */

    div[data-testid="stAlert"] {
        border-radius: 14px;
        border: none;

        font-size: 14px;
    }


    /* ---------- RIEPILOGO ---------- */

    .appointment-card {
        background: rgba(255,255,255,0.94);

        border: 1px solid rgba(0,0,0,0.08);

        border-radius: 22px;

        padding: 24px;

        margin-top: 22px;
        margin-bottom: 8px;

        box-shadow:
            0 10px 35px rgba(0,0,0,0.06);
    }

    .available {
        display: inline-flex;
        align-items: center;

        background: #e8f7ed;
        color: #147a35;

        border-radius: 100px;

        padding: 6px 11px;

        font-size: 13px;
        font-weight: 650;

        margin-bottom: 17px;
    }

    .appointment-date {
        color: #1d1d1f;

        font-size: 19px;
        font-weight: 600;

        margin-bottom: 4px;
    }

    .appointment-time {
        color: #1d1d1f;

        font-size: 30px;
        font-weight: 700;

        letter-spacing: -0.8px;

        margin-bottom: 15px;
    }

    .appointment-pharmacy {
        color: #6e6e73;

        font-size: 15px;
        line-height: 1.5;
    }


    /* ---------- CONFERMA ---------- */

    .success-card {
        text-align: center;

        background: white;

        border: 1px solid rgba(0,0,0,0.07);

        border-radius: 24px;

        padding: 30px 22px;

        margin-top: 25px;

        box-shadow:
            0 12px 40px rgba(0,0,0,0.06);
    }

    .success-icon {
        width: 56px;
        height: 56px;

        display: flex;
        align-items: center;
        justify-content: center;

        margin: 0 auto 18px auto;

        border-radius: 50%;

        background: #e8f7ed;
        color: #147a35;

        font-size: 27px;
        font-weight: 700;
    }

    .success-title {
        color: #1d1d1f;

        font-size: 23px;
        font-weight: 700;

        letter-spacing: -0.5px;
    }

    .success-text {
        color: #6e6e73;

        font-size: 15px;
        line-height: 1.5;

        margin-top: 8px;
    }


    /* ---------- MOBILE ---------- */

    @media (max-width: 640px) {

        .block-container {
            padding-top: 1.3rem;
            padding-left: 16px;
            padding-right: 16px;
        }

        .booking-hero {
            margin-bottom: 27px;
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

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="booking-hero">

        <div class="booking-icon">
            ◉
        </div>

        <div class="booking-title">
            Prenota una visita
        </div>

        <div class="booking-subtitle">
            Scegli il momento più comodo per incontrarci.
        </div>

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

st.caption("Nome farmacia e CAP sono obbligatori.")


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
# CALCOLO DISPONIBILITÀ
# =========================================================

giorno_valido = data_appuntamento.weekday() < 5

slots = []

if not giorno_valido:

    st.warning(
        "Le visite sono disponibili dal lunedì al venerdì."
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
        st.caption("1 orario disponibile")
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
# SE CAMBIANO I DATI, INVALIDIAMO LA VERIFICA PRECEDENTE
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
# VERIFICA
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
                    "Questa fascia è stata appena "
                    "occupata. Scegli un altro orario."
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

    st.markdown(
        f"""
        <div class="appointment-card">

            <div class="available">
                ✓ Disponibile
            </div>

            <div class="appointment-date">
                {data_testo}
            </div>

            <div class="appointment-time">
                {orario_testo}
            </div>

            <div class="appointment-pharmacy">
                <strong>{nome_farmacia}</strong><br>
                CAP {cap}<br>
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
            # prima della prenotazione

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
                    "prenotato. Scegline un altro."
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

                st.markdown(
                    f"""
                    <div class="success-card">

                        <div class="success-icon">
                            ✓
                        </div>

                        <div class="success-title">
                            Appuntamento confermato
                        </div>

                        <div class="success-text">
                            {data_testo}<br>
                            <strong>{orario_testo}</strong><br><br>
                            {nome_farmacia}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.balloons()

        except Exception:

            st.error(
                "Non è stato possibile registrare "
                "l'appuntamento. Riprova."
            )
