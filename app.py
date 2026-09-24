from datetime import date

import streamlit as st

from booking import (
    get_available_slots,
    format_slot
)

from google_calendar import (
    create_appointment
)


# --------------------------------------------------
# CONFIGURAZIONE
# --------------------------------------------------

st.set_page_config(
    page_title="Prenota una visita",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "slot_verificato" not in st.session_state:
    st.session_state.slot_verificato = None

if "prenotazione_completata" not in st.session_state:
    st.session_state.prenotazione_completata = False


# --------------------------------------------------
# CSS MOBILE-FIRST
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 600px;
        padding-top: 1rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 1.8rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        margin-top: 1.2rem !important;
    }

    input {
        font-size: 16px !important;
    }

    div[data-testid="stButton"] button {
        width: 100%;
        min-height: 52px;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 10px;
    }

    div[data-baseweb="select"] {
        min-height: 48px;
    }

    @media (max-width: 640px) {

        .block-container {
            padding-top: 0.7rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        h1 {
            font-size: 1.6rem !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# TITOLO
# --------------------------------------------------

st.title("Prenota una visita")

st.caption(
    "Scegli giorno e orario disponibili."
)


# --------------------------------------------------
# DATI FARMACIA
# --------------------------------------------------

st.subheader("Farmacia")

nome_farmacia = st.text_input(
    "Nome farmacia *",
    placeholder="Es. Farmacia Centrale"
)

cap = st.text_input(
    "CAP *",
    max_chars=5,
    placeholder="Es. 80100"
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
    "120 minuti": 120
}

durata_label = st.selectbox(
    "Durata dell'appuntamento *",
    options=list(durate.keys()),
    index=3
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
    format="DD/MM/YYYY"
)


# --------------------------------------------------
# DISPONIBILITÀ
# --------------------------------------------------

giorno_valido = (
    data_appuntamento.weekday() < 5
)

slots = []

if not giorno_valido:

    st.warning(
        "Gli appuntamenti sono disponibili "
        "dal lunedì al venerdì."
    )

else:

    try:

        slots = get_available_slots(
            data_appuntamento,
            durata
        )

    except Exception:

        st.error(
            "Non è stato possibile controllare "
            "Google Calendar."
        )


# --------------------------------------------------
# MENU ORARIO
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
            format_func=format_slot
        )

    else:

        st.info(
            "Nessun orario disponibile "
            "per questa data."
        )


# --------------------------------------------------
# CONTATTI
# --------------------------------------------------

st.subheader("Contatti")

referente = st.text_input(
    "Referente",
    placeholder="Nome e cognome"
)

telefono = st.text_input(
    "Telefono",
    placeholder="Es. 333 1234567"
)

email = st.text_input(
    "Email",
    placeholder="nome@farmacia.it"
)

st.caption(
    "* Nome farmacia e CAP sono obbligatori"
)


# --------------------------------------------------
# RIEPILOGO
# --------------------------------------------------

if slot_selezionato:

    st.divider()

    st.write(
        "### Riepilogo"
    )

    st.write(
        f"**Farmacia:** {nome_farmacia or '-'}"
    )

    st.write(
        f"**CAP:** {cap or '-'}"
    )

    st.write(
        f"**Data:** "
        f"{data_appuntamento.strftime('%d/%m/%Y')}"
    )

    st.write(
        f"**Orario:** "
        f"{format_slot(slot_selezionato)}"
    )

    st.write(
        f"**Durata:** {durata} minuti"
    )


# --------------------------------------------------
# VERIFICA DISPONIBILITÀ
# --------------------------------------------------

verifica = st.button(
    "Verifica disponibilità",
    type="primary",
    use_container_width=True,
    disabled=slot_selezionato is None
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

            # Rileggiamo Google Calendar
            # proprio in questo momento

            slots_aggiornati = (
                get_available_slots(
                    data_appuntamento,
                    durata
                )
            )

            ancora_disponibile = any(
                slot["start"]
                == slot_selezionato["start"]
                and
                slot["end"]
                == slot_selezionato["end"]

                for slot
                in slots_aggiornati
            )

            if ancora_disponibile:

                st.session_state.slot_verificato = {
                    "start":
                        slot_selezionato["start"],

                    "end":
                        slot_selezionato["end"]
                }

                st.success(
                    "Fascia disponibile."
                )

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
                "Errore durante la verifica "
                "della disponibilità."
            )


# --------------------------------------------------
# PRENOTAZIONE
# --------------------------------------------------

if st.session_state.slot_verificato:

    st.info(
        "La fascia è disponibile. "
        "Premi il pulsante sotto per confermare."
    )

    prenota = st.button(
        "Prenota appuntamento",
        use_container_width=True
    )

    if prenota:

        try:

            # Ultimo controllo prima
            # della scrittura su Calendar

            slots_finali = (
                get_available_slots(
                    data_appuntamento,
                    durata
                )
            )

            slot_salvato = (
                st.session_state.slot_verificato
            )

            ancora_libero = any(

                slot["start"]
                == slot_salvato["start"]
                and
                slot["end"]
                == slot_salvato["end"]

                for slot
                in slots_finali
            )

            if not ancora_libero:

                st.session_state.slot_verificato = None

                st.error(
                    "La fascia è stata appena "
                    "occupata. Seleziona un nuovo "
                    "orario."
                )

                st.rerun()

            else:

                evento = create_appointment(

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
                        referente,

                    telefono=
                        telefono,

                    email=
                        email
                )

                st.session_state.slot_verificato = None
                st.session_state.prenotazione_completata = True

                st.success(
                    "Appuntamento confermato."
                )

                st.write(
                    f"**{data_appuntamento.strftime('%d/%m/%Y')}**"
                )

                st.write(
                    f"**{format_slot(slot_salvato)}**"
                )

                st.write(
                    f"Farmacia: **{nome_farmacia}**"
                )

                st.info(
                    "La visita è stata registrata "
                    "nel calendario."
                )

        except Exception:

            st.error(
                "Non è stato possibile registrare "
                "l'appuntamento. Riprova."
            )
