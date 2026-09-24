import streamlit as st

st.set_page_config(
    page_title="Prenota una visita",
    page_icon="📅",
    layout="centered"
)

st.title("Prenota una visita")
st.write(
    "Scegli la durata dell'incontro e trova una fascia disponibile."
)

st.divider()

# -------------------------
# DATI FARMACIA
# -------------------------

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

# -------------------------
# DURATA
# -------------------------

st.subheader("Durata della visita")

durata_opzione = st.radio(
    "Quanto tempo desideri dedicare all'appuntamento?",
    ["30 min", "45 min", "60 min", "75 min", "90+ min"],
    horizontal=True
)

durata = None

if durata_opzione == "30 min":
    durata = 30

elif durata_opzione == "45 min":
    durata = 45

elif durata_opzione == "60 min":
    durata = 60

elif durata_opzione == "75 min":
    durata = 75

elif durata_opzione == "90+ min":
    durata = st.selectbox(
        "Scegli la durata",
        [90, 105, 120],
        format_func=lambda x: f"{x} minuti"
    )

# -------------------------
# DATI FACOLTATIVI
# -------------------------

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

st.caption("* Campi obbligatori")

st.divider()

# -------------------------
# RICERCA DISPONIBILITÀ
# -------------------------

if st.button(
    "Cerca disponibilità",
    type="primary",
    use_container_width=True
):

    errori = []

    if not nome_farmacia.strip():
        errori.append("Inserisci il nome della farmacia.")

    if not cap.strip():
        errori.append("Inserisci il CAP.")

    elif not cap.isdigit() or len(cap) != 5:
        errori.append("Il CAP deve essere composto da 5 numeri.")

    if errori:

        for errore in errori:
            st.error(errore)

    else:

        st.success("Dati corretti.")

        st.write("### Riepilogo")

        st.write(f"**Farmacia:** {nome_farmacia}")
        st.write(f"**CAP:** {cap}")
        st.write(f"**Durata:** {durata} minuti")

        if referente:
            st.write(f"**Referente:** {referente}")

        if telefono:
            st.write(f"**Telefono:** {telefono}")

        if email:
            st.write(f"**Email:** {email}")

        st.info(
            "Nel prossimo passaggio verranno mostrate "
            "le disponibilità del calendario."
        )
