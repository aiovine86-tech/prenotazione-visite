from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import html
import base64

import pandas as pd
import streamlit as st

from booking import (
    get_available_slots,
    format_slot,
)

from google_calendar import (
    create_appointment,
    get_territorial_appointments,
)

from pushover_service import (
    send_booking_notification,
)

from vicinanze import (
    normalizza_cap,
    normalizza_comune,
    sono_vicini,
)
# =========================================================
# CONFIGURAZIONE
# =========================================================

TIMEZONE = ZoneInfo("Europe/Rome")
# =========================================================
# ARCHIVIO FARMACIE
# =========================================================

@st.cache_data
def load_farmacie():
    """
    Carica l'archivio delle farmacie da farmacie.xlsx.
    """

    df = pd.read_excel(
        "farmacie.xlsx",
        sheet_name="Archivio definitivo",
        dtype=str,
    )

    # Elimina eventuali spazi dai nomi delle colonne
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # CAP sempre normalizzato a 5 cifre
    df["CAP"] = (
        df["CAP"]
        .fillna("")
        .apply(normalizza_cap)
    )

    # Comune normalizzato secondo le stesse regole
    # utilizzate da vicinanze.py
    df["Comune_normalizzato"] = (
        df["Comune"]
        .fillna("")
        .apply(normalizza_comune)
    )

    # Nome farmacia:
    # usiamo Nome finale quando presente,
    # altrimenti Nome originale.
    nome_finale = (
        df["Nome finale"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    nome_originale = (
        df["Nome originale"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Nome_farmacia"] = nome_finale.where(
        nome_finale != "",
        nome_originale,
    )

    # Correzione territoriale già concordata:
    # Frattamaggiore deve essere trattata come 80027.
    mask_frattamaggiore = (
        df["Comune_normalizzato"]
        == "FRATTAMAGGIORE"
    )

    df.loc[
        mask_frattamaggiore,
        "CAP"
    ] = "80027"

    # Manteniamo solo record utilizzabili
    df = df[
        (df["CAP"] != "")
        & (df["Comune_normalizzato"] != "")
        & (df["Nome_farmacia"] != "")
    ].copy()

    # Evita eventuali duplicati nell'elenco mostrato
    df = df.drop_duplicates(
        subset=[
            "CAP",
            "Comune_normalizzato",
            "Nome_farmacia",
        ]
    )

    return df


farmacie_df = load_farmacie()


# =========================================================
# DATE CONSIGLIATE
# =========================================================

def get_recommended_dates(cap, comune, durata, oggi, giorni=7, max_risultati=3):
    if not cap or not comune:
        return []

    fine_periodo = oggi + timedelta(days=giorni - 1)
    try:
        appuntamenti = get_territorial_appointments(oggi, fine_periodo)
    except Exception as e:
        print("Errore lettura appuntamenti territoriali:", e)
        return []

    risultati = []
    for offset in range(giorni):
        giorno = oggi + timedelta(days=offset)
        if giorno.weekday() >= 5:
            continue
        try:
            slots_giorno = get_available_slots(giorno, durata)
        except Exception as e:
            print("Errore disponibilità data consigliata:", giorno, e)
            continue

        if giorno == oggi:
            now = datetime.now(TIMEZONE)
            slots_giorno = [s for s in slots_giorno if s["start"] > now]
        if not slots_giorno:
            continue

        visite_vicine = []
        for appuntamento in appuntamenti:
            if appuntamento["start"].date() != giorno:
                continue
            cap_a = appuntamento.get("cap", "").strip()
            comune_a = appuntamento.get("comune", "").strip()
            if not cap_a or not comune_a:
                continue
            if sono_vicini(cap, comune, cap_a, comune_a):
                visite_vicine.append(appuntamento)
        if not visite_vicine:
            continue

        miglior_gap = None
        miglior_slot = None
        for slot in slots_giorno:
            for visita in visite_vicine:
                if slot["end"] <= visita["start"]:
                    gap = (visita["start"] - slot["end"]).total_seconds() / 60
                elif slot["start"] >= visita["end"]:
                    gap = (slot["start"] - visita["end"]).total_seconds() / 60
                else:
                    continue
                if miglior_gap is None or gap < miglior_gap:
                    miglior_gap = gap
                    miglior_slot = slot

        if miglior_slot is not None:
            risultati.append({
                "data": giorno,
                "numero_visite_vicine": len(visite_vicine),
                "miglior_gap_minuti": miglior_gap,
                "miglior_slot": miglior_slot,
            })

    risultati.sort(key=lambda x: (-x["numero_visite_vicine"], x["miglior_gap_minuti"], x["data"]))
    return risultati[:max_risultati]


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
    margin: 0 auto;

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

    padding: 10px 15px 10px 10px;

    border-radius: 18px;

    background: rgba(255,255,255,.82);

    border: 1px solid rgba(16,24,40,.06);

    box-shadow:
        0 8px 26px
        rgba(16,24,40,.055);

    backdrop-filter: blur(16px);
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
   INPUT
   ======================================================== */

label[data-testid="stWidgetLabel"] p {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #475467 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {

    background: rgba(255,255,255,.96) !important;

    border: 1px solid #e4e7ec !important;

    border-radius: 14px !important;

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

    border-color: #34c759 !important;

    box-shadow:
        0 0 0 3px
        rgba(52,199,89,.10)
        !important;
}

div[data-testid="stDateInput"] input {

    background: rgba(255,255,255,.96) !important;

    border-radius: 14px !important;
}


/* ========================================================
   DISPONIBILITÀ
   ======================================================== */

.availability-card {

    display: flex;
    align-items: center;

    margin-top: 4px;
    margin-bottom: 14px;

    padding: 12px 14px;

    border-radius: 14px;

    background: rgba(52,199,89,.075);

    border: 1px solid rgba(52,199,89,.15);

    color: #18743e;

    font-size: 13px;
    font-weight: 620;
}


/* ========================================================
   ALERT
   ======================================================== */

div[data-testid="stAlert"] {

    border-radius: 14px;

    border: 1px solid rgba(16,24,40,.05);
}


/* ========================================================
   PULSANTI
   ======================================================== */

div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {

    min-height: 50px;

    border-radius: 14px !important;

    font-size: 15px !important;

    font-weight: 680 !important;

    transition:
        transform .12s ease,
        box-shadow .15s ease;
}

div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {

    transform: translateY(-1px);
}

div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stDownloadButton"] button[kind="primary"] {

    background:
        linear-gradient(
            135deg,
            #34c759 0%,
            #209447 100%
        )
        !important;

    color: white !important;

    border: none !important;

    box-shadow:
        0 10px 24px
        rgba(32,148,71,.20)
        !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button[kind="primary"]:hover {

    box-shadow:
        0 13px 28px
        rgba(32,148,71,.25)
        !important;
}


/* ========================================================
   SUCCESS
   ======================================================== */

.success-card {

    margin-top: 18px;

    padding: 26px;

    border-radius: 24px;

    background: rgba(255,255,255,.90);

    border: 1px solid rgba(52,199,89,.16);

    box-shadow:
        0 18px 45px
        rgba(16,24,40,.07);

    backdrop-filter: blur(18px);
}

.success-icon {

    width: 54px;
    height: 54px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #34c759,
            #1e9b4a
        );

    color: white;

    font-size: 27px;
    font-weight: 700;

    margin-bottom: 17px;

    box-shadow:
        0 9px 22px
        rgba(52,199,89,.20);
}

.success-title {

    font-size: 25px;

    font-weight: 750;

    letter-spacing: -.6px;

    color: #101828;

    margin-bottom: 7px;
}

.success-text {

    color: #667085;

    font-size: 14px;

    line-height: 1.55;

    margin-bottom: 18px;
}

.success-details {

    padding: 16px;

    border-radius: 15px;

    background: #f8faf9;

    border: 1px solid #edf1ee;

    color: #344054;

    font-size: 14px;

    line-height: 1.9;
}


/* ========================================================
   CALENDARIO
   ======================================================== */

.calendar-help {

    text-align: center;

    color: #667085;

    font-size: 12px;

    line-height: 1.45;

    margin:
        4px 10px
        12px 10px;
}


/* ========================================================
   FOOTER
   ======================================================== */

.footer-note {

    text-align: center;

    max-width: 440px;

    margin: 30px auto 0 auto;

    color: #98a2b3;

    font-size: 11px;

    line-height: 1.5;
}


/* ========================================================
   MOBILE
   ======================================================== */

@media (max-width: 640px) {

    .block-container {

        padding-top: 1rem;

        padding-left: 1rem;

        padding-right: 1rem;

        padding-bottom: 2.5rem;
    }

    .profile-header {

        margin-bottom: 1.55rem;
    }

    .profile-monogram {

        width: 60px;

        height: 60px;

        border-radius: 19px;

        font-size: 21px;

        margin-bottom: 14px;
    }

    .booking-title {

        font-size: 28px;

        letter-spacing: -.9px;
    }

    .profile-description {

        font-size: 14px;

        padding: 0 8px;
    }

    .profile-card {

        margin-top: 17px;
    }

    .section-header {

        margin-top: 24px;

        margin-bottom: 11px;
    }

    .section-title {

        font-size: 17px;
    }

    .success-card {

        padding: 21px;
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
def get_profile_image_base64():
    try:
        with open("alessandro.png", "rb") as image_file:
            encoded = base64.b64encode(
                image_file.read()
            ).decode()

        return f"data:image/png;base64,{encoded}"

    except Exception as e:
        print("Errore caricamento foto profilo:", e)
        return ""



def render_small_header():

    profile_image = get_profile_image_base64()

    if profile_image:

        avatar = (
            '<div class="profile-monogram" '
            'style="padding:0; overflow:hidden;">'
            f'<img src="{profile_image}" '
            'style="width:100%; height:100%; '
            'object-fit:cover; display:block;">'
            '</div>'
        )

    else:

        avatar = (
            '<div class="profile-monogram">'
            'AI'
            '</div>'
        )

    markup = (
        '<div class="profile-header">'
        f'{avatar}'
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
# FILE CALENDARIO .ICS
# =========================================================

def escape_ics_text(value):

    value = str(value)

    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace("\r\n", "\\n")
    value = value.replace("\n", "\\n")

    return value


def create_ics_file(prenotazione):

    start = prenotazione["start"]
    end = prenotazione["end"]

    nome_farmacia = prenotazione["nome_farmacia"]
    cap = prenotazione["cap"]
    comune = prenotazione.get("comune", "")

    start_ics = start.strftime(
        "%Y%m%dT%H%M%S"
    )

    end_ics = end.strftime(
        "%Y%m%dT%H%M%S"
    )

    farmacia_ics = escape_ics_text(
        nome_farmacia
    )

    cap_ics = escape_ics_text(
        cap
    )

    comune_ics = escape_ics_text(
        comune
    )

    summary = escape_ics_text(
        "Appuntamento con Alessandro Iovine"
    )

    description = (
        "Appuntamento con Alessandro Iovine\\n"
        "Sales Manager\\n"
        "PIC · CONTROL · EFFERDENT\\n"
        f"Farmacia: {farmacia_ics}\\n"
        f"CAP: {cap_ics}\n"
        f"Comune: {comune_ics}"
    )

    location = (
        f"{farmacia_ics} - {comune_ics} - CAP {cap_ics}"
    )

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Alessandro Iovine//Prenotazione Visite//IT\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"

        "BEGIN:VTIMEZONE\r\n"
        "TZID:Europe/Rome\r\n"
        "X-LIC-LOCATION:Europe/Rome\r\n"
        "BEGIN:DAYLIGHT\r\n"
        "TZOFFSETFROM:+0100\r\n"
        "TZOFFSETTO:+0200\r\n"
        "TZNAME:CEST\r\n"
        "DTSTART:19700329T020000\r\n"
        "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\n"
        "END:DAYLIGHT\r\n"
        "BEGIN:STANDARD\r\n"
        "TZOFFSETFROM:+0200\r\n"
        "TZOFFSETTO:+0100\r\n"
        "TZNAME:CET\r\n"
        "DTSTART:19701025T030000\r\n"
        "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\n"
        "END:STANDARD\r\n"
        "END:VTIMEZONE\r\n"

        "BEGIN:VEVENT\r\n"
        f"DTSTART;TZID=Europe/Rome:{start_ics}\r\n"
        f"DTEND;TZID=Europe/Rome:{end_ics}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"DESCRIPTION:{description}\r\n"
        f"LOCATION:{location}\r\n"
        "STATUS:CONFIRMED\r\n"
        "END:VEVENT\r\n"

        "END:VCALENDAR\r\n"
    )

    return ics_content.encode(
        "utf-8"
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

    comune = html.escape(
        prenotazione.get("comune", "")
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

        '<div class="success-icon">'
        '✓'
        '</div>'

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
        f'{cap}<br>'

        f'<strong>Comune:</strong> '
        f'{comune}'

        '</div>'
        '</div>'
    )

    st.markdown(
        success_markup,
        unsafe_allow_html=True,
    )

    st.write("")

    # =====================================================
    # AGGIUNGI AL CALENDARIO DEL CLIENTE
    # =====================================================

    calendar_file = create_ics_file(
        prenotazione
    )

    st.download_button(
        label="Aggiungi al calendario",
        data=calendar_file,
        file_name="appuntamento-alessandro-iovine.ics",
        mime="text/calendar; charset=utf-8",
        use_container_width=True,
        type="primary",
    )

    st.markdown(
        (
            '<div class="calendar-help">'
            'Salva l’appuntamento anche '
            'nel calendario del tuo smartphone.'
            '</div>'
        ),
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
# HEADER
# =========================================================

def render_main_header():

    profile_image = get_profile_image_base64()

    if profile_image:
        avatar_grande = (
            '<div class="profile-monogram" '
            'style="padding:0; overflow:hidden; margin:0;">'
            f'<img src="{profile_image}" '
            'style="width:100%; height:100%; '
            'object-fit:cover; display:block;">'
            '</div>'
        )
    else:
        avatar_grande = (
            '<div class="profile-monogram" '
            'style="margin:0;">'
            'AI'
            '</div>'
        )

    markup = (
        '<div class="profile-header">'

        # FOTO + DATI SULLA STESSA RIGA
        '<div style="'
        'display:flex; '
        'align-items:center; '
        'justify-content:center; '
        'gap:16px; '
        'margin-bottom:22px;'
        '">'

        f'{avatar_grande}'

        '<div style="text-align:left;">'

        '<div class="profile-name" '
        'style="font-size:17px;">'
        'Alessandro Iovine'
        '</div>'

        '<div class="profile-role" '
        'style="font-size:13px; margin-top:3px;">'
        'Sales Manager'
        '</div>'

        '<div class="profile-brands" '
        'style="font-size:12px; margin-top:4px;">'
        'PIC · CONTROL · EFFERDENT'
        '</div>'

        '</div>'
        '</div>'

        # TITOLO
        '<div class="booking-title">'
        'Prenota un appuntamento'
        '</div>'

        '<div class="profile-description">'
        'Scegli giorno e orario per fissare '
        'un appuntamento direttamente presso la tua farmacia.'
        '</div>'

        '</div>'
    )

    st.markdown(
        markup,
        unsafe_allow_html=True,
    )render_main_header()

# =========================================================
# 1 - FARMACIA
# =========================================================

section_header(
    "1",
    "La tua farmacia",
    "Inserisci il CAP e seleziona la farmacia",
)

cap_input = st.text_input(
    "CAP *",
    placeholder="Es. 81030",
    max_chars=5,
)

cap = normalizza_cap(cap_input)

nome_farmacia = ""
comune = ""
farmacia_selezionata = None

OPZIONE_ALTRA_FARMACIA = "La mia farmacia non è presente"


# ---------------------------------------------------------
# CERCA FARMACIE PER CAP
# ---------------------------------------------------------

if cap_input:

    if (
        not cap_input.isdigit()
        or len(cap_input) != 5
    ):

        st.warning(
            "Inserisci un CAP valido di 5 cifre."
        )

    else:

        farmacie_cap = farmacie_df[
            farmacie_df["CAP"] == cap
        ].copy()

        # -------------------------------------------------
        # COMUNI ASSOCIATI AL CAP
        # -------------------------------------------------

        comuni_cap = (
            farmacie_cap["Comune_normalizzato"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        comuni_cap = sorted(
            {
                comune_item
                for comune_item in comuni_cap
                if comune_item
            }
        )

        # -------------------------------------------------
        # SE NON TROVIAMO FARMACIE PER QUESTO CAP
        # -------------------------------------------------

        if farmacie_cap.empty:

            st.info(
                "La tua farmacia non è ancora presente "
                "nel nostro archivio. "
                "Puoi inserirla manualmente."
            )

            nome_farmacia = st.text_input(
                "Nome farmacia *",
                placeholder="Es. Farmacia Rossi",
                key="nome_farmacia_manuale_senza_archivio",
            )

            # Se il CAP non esiste nell'archivio non possiamo
            # ricavare automaticamente il Comune.
            comune_manuale = st.text_input(
                "Comune *",
                placeholder="Es. Napoli",
                key="comune_manuale_senza_archivio",
            )

            if comune_manuale.strip():

                comune = normalizza_comune(
                    comune_manuale
                )

                st.caption(
                    f"CAP {cap} · "
                    f"{comune.title()}"
                )

        # -------------------------------------------------
        # FARMACIE PRESENTI NELL'ARCHIVIO
        # -------------------------------------------------

        else:

            farmacie_cap = farmacie_cap.sort_values(
                by=[
                    "Comune_normalizzato",
                    "Nome_farmacia",
                ]
            )

            records = farmacie_cap.to_dict(
                orient="records"
            )

            # Creiamo opzioni leggibili.
            # L'ultima permette l'inserimento manuale.
            opzioni_farmacia = []

            for record in records:

                opzioni_farmacia.append(
                    {
                        "tipo": "archivio",
                        "nome": record[
                            "Nome_farmacia"
                        ],
                        "comune": record[
                            "Comune_normalizzato"
                        ],
                        "record": record,
                    }
                )

            opzioni_farmacia.append(
                {
                    "tipo": "manuale",
                    "nome": OPZIONE_ALTRA_FARMACIA,
                    "comune": "",
                    "record": None,
                }
            )

            farmacia_selezionata = st.selectbox(
                "Farmacia *",
                opzioni_farmacia,
                index=None,
                placeholder="Seleziona la farmacia",
                format_func=lambda x: (
                    (
                        f'{x["nome"]} · '
                        f'{x["comune"].title()}'
                    )
                    if x["tipo"] == "archivio"
                    else x["nome"]
                ),
            )

            # =============================================
            # FARMACIA PRESENTE NELL'ARCHIVIO
            # =============================================

            if (
                farmacia_selezionata
                and farmacia_selezionata[
                    "tipo"
                ] == "archivio"
            ):

                nome_farmacia = (
                    farmacia_selezionata[
                        "nome"
                    ]
                    .strip()
                )

                comune = (
                    farmacia_selezionata[
                        "comune"
                    ]
                    .strip()
                )

                st.caption(
                    f"CAP {cap} · "
                    f"{comune.title()}"
                )

            # =============================================
            # FARMACIA NON PRESENTE
            # =============================================

            elif (
                farmacia_selezionata
                and farmacia_selezionata[
                    "tipo"
                ] == "manuale"
            ):

                nome_farmacia = st.text_input(
                    "Nome farmacia *",
                    placeholder="Es. Farmacia Rossi",
                    key="nome_farmacia_manuale",
                )

                # -----------------------------------------
                # UN SOLO COMUNE PER QUESTO CAP
                # -----------------------------------------

                if len(comuni_cap) == 1:

                    comune = comuni_cap[0]

                    st.caption(
                        f"Comune: "
                        f"{comune.title()}"
                    )

                # -----------------------------------------
                # PIÙ COMUNI PER LO STESSO CAP
                # -----------------------------------------

                elif len(comuni_cap) > 1:

                    comune_scelto = st.selectbox(
                        "Comune *",
                        comuni_cap,
                        index=None,
                        placeholder="Seleziona il Comune",
                        format_func=lambda x: x.title(),
                    )

                    if comune_scelto:

                        comune = comune_scelto

                # -----------------------------------------
                # NESSUN COMUNE DISPONIBILE
                # -----------------------------------------

                else:

                    comune_manuale = st.text_input(
                        "Comune *",
                        placeholder="Es. Napoli",
                        key="comune_manuale",
                    )

                    if comune_manuale.strip():

                        comune = normalizza_comune(
                            comune_manuale
                        )

                # Mostra riepilogo solo quando abbiamo
                # sia farmacia sia Comune.
                if (
                    nome_farmacia.strip()
                    and comune
                ):

                    st.caption(
                        f"CAP {cap} · "
                        f"{comune.title()}"
                    )

# =========================================================
# 2 - APPUNTAMENTO
# =========================================================

section_header(
    "2",
    "Quando preferisci incontrarci?",
    "Scegli durata, data e orario",
)

durata = st.selectbox(
    "Durata dell'appuntamento",
    [30, 45, 60, 75, 90, 105, 120],
    index=3,
    format_func=lambda x: f"{x} minuti",
)

oggi = datetime.now(TIMEZONE).date()

recommended_dates = []
if nome_farmacia and cap and comune:
    recommended_dates = get_recommended_dates(cap, comune, durata, oggi)

if recommended_dates:
    st.markdown("**Date consigliate in base alle visite già in zona**")
    opzioni = [r["data"] for r in recommended_dates]
    data_consigliata = st.radio(
        "Scegli una data consigliata",
        opzioni,
        index=None,
        format_func=lambda d: next(
            f"{d.strftime('%d/%m/%Y')} · {r['numero_visite_vicine']} visita{'e' if r['numero_visite_vicine'] != 1 else ''} in zona"
            for r in recommended_dates if r["data"] == d
        ),
    )
    altra_data = st.checkbox("Preferisci un'altra data?")
    if altra_data or data_consigliata is None:
        data = st.date_input("Data", min_value=oggi, value=oggi)
    else:
        data = data_consigliata
else:
    if nome_farmacia:
        st.caption("Nessuna data con visite vicine trovata nei prossimi 7 giorni. Puoi scegliere liberamente la data.")
    data = st.date_input("Data", min_value=oggi, value=oggi)


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

    except Exception as e:

        print(
            "Errore verifica disponibilità:",
            e,
        )

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
            "Seleziona la farmacia."
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

            updated_slots = get_available_slots(
                data,
                durata,
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
                slot["start"] == selected_slot["start"]
                and
                slot["end"] == selected_slot["end"]
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

                    comune=
                        comune.strip(),

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
                # PUSHOVER
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

                except Exception as e:

                    print(
                        "Errore invio Pushover:",
                        e,
                    )

                # =========================================
                # SALVA CONFERMA
                # =========================================

                st.session_state.ultima_prenotazione = {

                    "nome_farmacia":
                        nome_farmacia.strip(),

                    "cap":
                        cap.strip(),

                    "comune":
                        comune.strip(),

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

        except Exception as e:

            print(
                "Errore prenotazione:",
                e,
            )

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
