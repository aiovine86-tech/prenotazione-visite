from datetime import date, timedelta

import streamlit as st

from booking import get_available_slots, format_slot


st.set_page_config(
    page_title="Prenota una visita",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# STILE MOBILE-FIRST
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 600px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.8rem !important;
            line-height: 1.2 !important;
            margin-bottom: 0.3rem !important;
        }

        h2, h3 {
            margin-top: 1.2rem !important;
        }

        div[data-testid="stButton"] button {
            min-height: 52px;
            font-size: 1.05rem;
            font-weight: 600;
            border-radius: 10px;
        }

        div[data-baseweb="select"] {
            min-height: 48px;
        }

        input {
            font-size: 16px !important;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 0.8rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            h1 {
                font-size: 1.65rem !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# TESTATA
# --------------------------------------------------

st.title("Prenota una visita")

st.caption(
    "Scegli giorno e orario in pochi secondi."
)


# --------------------------------------------------
# DATI FARMACIA
# --------------------------------------------------

st.subheader("Farmacia")

nome_farmacia = st.text_input(
    "Nome farmacia *",
    placeholder="Es. Farmacia Centrale",
)

cap = st.text_input(
    "CAP *",
    max_chars=5,
    placeholder="Es. 80100",
)


# --------------------------------------------------
# DURATA
# --------------------------------------------------

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
    "Durata dell'appuntamento *",
    options=list(durate.keys()),
    index=3,
)

durata = durate[durata_label]


# --------------------------------------------------
# DATA
# --------------------------------------------------

oggi = date.today()

data_appuntamento = st.date_input(
    "Data *",
    value=oggi,
    min_value=oggi,
    format="DD/MM/YYYY",
)


# --------------------------------------------------
# CONTROLLO DATA
# --------------------------------------------------

giorno_valido = data_appuntamento.weekday() < 5

if not giorno_valido:

    st.warning(
        "Gli appuntamenti sono disponibili "
        "dal lunedì al venerdì."
    )

    slots = []

else:

    try:

        slots = get_available_slots(
            data_appuntamento,
            durata
        )

    except Exception:

        slots = []

        st.error(
            "Non è stato possibile controllare "
            "le disponibilità del calendario."
        )


# --------------------------------------------------
# MENU ORARI
# --------------------------------------------------

slot_selezionato = None

if giorno_valido:

    if slots:

        st.caption(
            f"{len(slots)} orari disponibili"
        )

        slot_selezionato = st.selectbox(
            "Orario disponibile *",
            options=slots,
            format_func=format_slot,
        )

    else:

        st.info(
            "Nessun orario disponibile per "
            "questa data e questa durata."
        )


# --------------------------------------------------
# CONTATTI
# --------------------------------------------------

st.subheader("Contatti")

referente = st.text_input(
    "Referente",
    placeholder="Nome e cognome",
)

telefono = st.text_input(
    "Telefono",
    placeholder="Es. 333 1234567",
)

email = st.text_input(
    "Email",
    placeholder="nome@farmacia.it",
)

st.caption("* Campi obbligatori")


# --------------------------------------------------
# CONFERMA
# --------------------------------------------------

st.divider()

if slot_selezionato:

    st.write("**Riepilogo appuntamento**")

    st.write(
        f"**{data_appuntamento.strftime('%d/%m/%Y')}**"
    )

    st.write(
        f"**{format_slot(slot_selezionato)}**"
    )

    st.write(
        f"{durata} minuti"
    )


conferma = st.button(
    "Conferma appuntamento",
    type="primary",
    use_container_width=True,
    disabled=slot_selezionato is None,
)


# --------------------------------------------------
# VALIDAZIONE
# --------------------------------------------------

if conferma:

    errori = []

    nome_farmacia = nome_farmacia.strip()
    cap = cap.strip()

    if not nome_farmacia:
        errori.append(
            "Inserisci il nome della farmacia."
        )

    if not cap:
        errori.append(
            "Inserisci il CAP."
        )

    elif not cap.isdigit() or len(cap) != 5:
        errori.append(
            "Inserisci un CAP valido di 5 cifre."
        )

    if errori:

        for errore in errori:
            st.error(errore)

    else:

        st.success(
            "I dati sono validi. "
            "La prenotazione è pronta per essere registrata."
        )

        st.info(
            "Nel prossimo passaggio collegheremo "
            "questo pulsante alla creazione automatica "
            "dell'evento su Google Calendar."
        )
