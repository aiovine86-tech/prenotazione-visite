from datetime import date, datetime
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
    page_title="Prenota una visita",
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


/* HERO */

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
        0 5px 18px rgba(0,0,0,0.12);
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


/* TITOLI */

h3 {
    color: #1d1d1f !important;

    font-size: 19px !important;

    font-weight: 650 !important;

    letter-spacing: -0.3px !important;

    margin-top: 34px !important;
    margin-bottom: 10px !important;
}


/* LABEL */

div[data-testid="stWidgetLabel"] p {
    color: #3a3a3c !important;

    font-size: 14px !important;
    font-weight: 500 !important;
}


/* INPUT */

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

    -webkit-text-fill-color: #1d1d1f !important;

    font-size: 16px !important;

    min-height: 50px !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #86868b !important;

    -webkit-text-fill-color: #86868b !important;

    opacity: 1 !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: #0071e3 !important;

    box-shadow:
        0 0 0 3px rgba(0,113,227,0.12)
        !important;
}


/* SELECT */

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
        0 0 0 3px rgba(0,113,227,0.12)
        !important;
}


/* DATA */

div[data-testid="stDateInput"] input {
    background: #ffffff !important;

    color: #1d1d1f !important;

    -webkit-text-fill-color: #1d1d1f !important;

    font-size: 16px !important;
}


/* CAPTION */

div[data-testid="stCaptionContainer"] p {
    color: #86868b !important;
    font-size: 13px !important;
}


/* PULSANTE */

div[data-testid="stButton"] {
    margin-top: 22px;
}

div[data-testid="stButton"] button {
    width: 100% !important;

    min-height: 56px !important;

    border-radius: 15px !important;

    font-size: 16px !important;
    font-weight: 600 !important;

    border: none !important;

    transition:
        transform 0.12s ease,
        background 0.12s ease;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #1d1d1f !important;
    color: #ffffff !important;
}

div[data-testid="stButton"] button[kind="primary"] p {
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
}


/* ALERT */

div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: none !important;
}


/* NOTA DISPONIBILITÀ */

.availability-note {
    background: #ffffff;

    border: 1px solid rgba(0,0,0,0.06);

    border-radius: 14px;

    padding: 13px 15px;

    margin-top: 12px;

    color: #6e6e73;

    font-size: 13px;
    line-height: 1.45;
}


/* SUCCESS */

.success-card {
    text-align: center;

    background: #ffffff;

    border: 1px solid rgba(0,0,0,0.07);

    border-radius: 26px;

    padding: 36px 24px;

    margin-top: 20px;

    box-shadow:
        0 12px 40px rgba(0,0,0,0.06);
}

.success-icon {
    width: 62px;
    height: 62px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 20px auto;

    border-radius: 50%;

    background: #e8f7ed;
    color: #147a35;

    font-size: 30px;
    font-weight: 700;
}

.success-title {
    color: #1d1d1f;

    font-size: 25px;
    font-weight: 700;

    letter-spacing: -0.6px;
}

.success-pharmacy {
    color: #1d1d1f;

    font-size: 18px;
    font-weight: 600;

    margin-top: 22px;
}

.success-time {
    color: #1d1d1f;

    font-size: 28px;
    font-weight: 700;

    letter-spacing: -0.6px;

    margin-top: 7px;
}

.success-details {
    color: #6e6e73;

    font-size: 15px;
    line-height: 1.6;

    margin-top: 10px;
}


/* MOBILE */

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

    .success-card {
        padding: 30px 20px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SE PRENOTAZIONE COMPLETATA:
# MOSTRIAMO SOLO LA CONFERMA
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
<div class="booking-icon">✓</div>
<div class="booking-title">Prenotazione completata</div>
<div class="booking-subtitle">La visita è stata registrata correttamente.</div>
</div>

<div class="success-card">
<div class="success-icon">✓</div>
<div class="success-title">Appuntamento confermato</div>
<div class="success-pharmacy">{farmacia_html}</div>
<div class="success-time">{dati["orario"]}</div>
<div class="success-details">
{dati["data"]}<br>
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
<div class="booking-icon">◉</div>
<div class="booking-title">Prenota una visita</div>
<div class="booking-subtitle">Scegli giorno e orario più comodi per te.</div>
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


oggi = datetime.now(TIMEZONE).date()


data_appuntamento = st.date_input(
    "Data",
    value=oggi,
    min_value=oggi,
    format="DD/MM/YYYY",
)


# =========================================================
# CONTROLLO GIORNO
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


        # -------------------------------------------------
        # SE È OGGI:
        # ELIMINIAMO GLI ORARI GIÀ PASSATI
        # -------------------------------------------------

        if data_appuntamento == oggi:

            adesso = datetime.now(TIMEZONE)

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
# PICCOLA NOTA
# =========================================================

if slot_selezionato:

    st.markdown(
        """
<div class="availability-note">
L'orario selezionato risulta disponibile.
La disponibilità verrà ricontrollata automaticamente
prima della conferma.
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# PRENOTA
# =========================================================

prenota = st.button(
    "Prenota appuntamento",
    type="primary",
    use_container_width=True,
    disabled=slot_selezionato is None,
)


# =========================================================
# GESTIONE PRENOTAZIONE
# =========================================================

if prenota:

    nome_pulito = nome_farmacia.strip()
    cap_pulito = cap.strip()

    errori = []


    # -----------------------------------------------------
    # VALIDAZIONE
    # -----------------------------------------------------

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

        for errore in errori:
            st.error(errore)


    else:

        try:

            # =============================================
            # RICONTROLLO SILENZIOSO GOOGLE CALENDAR
            # =============================================

            slots_finali = get_available_slots(
                data_appuntamento,
                durata,
            )


            # Anche nel controllo finale
            # eliminiamo eventuali slot ormai trascorsi.

            if data_appuntamento == oggi:

                adesso = datetime.now(TIMEZONE)

                slots_finali = [
                    slot
                    for slot in slots_finali
                    if slot["start"] > adesso
                ]


            ancora_libero = any(
                slot["start"]
                == slot_selezionato["start"]
                and
                slot["end"]
                == slot_selezionato["end"]

                for slot
                in slots_finali
            )


            # =============================================
            # SLOT NON PIÙ DISPONIBILE
            # =============================================

            if not ancora_libero:

                st.error(
                    "Questo orario è stato appena "
                    "occupato. Scegli un altro orario."
                )

                st.rerun()


            # =============================================
            # CREA EVENTO
            # =============================================

            create_appointment(
                nome_farmacia=nome_pulito,
                cap=cap_pulito,

                start_datetime=
                    slot_selezionato["start"],

                end_datetime=
                    slot_selezionato["end"],

                durata=durata,

                referente=
                    referente.strip(),

                telefono=
                    telefono.strip(),

                email=
                    email.strip(),
            )


            # =============================================
            # SALVA DATI PER SCHERMATA FINALE
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
