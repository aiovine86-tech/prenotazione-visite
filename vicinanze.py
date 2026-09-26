# vicinanze.py
#
# Mappa manuale delle vicinanze territoriali per il sistema
# di prenotazione visite.
#
# PRINCIPI:
# - la chiave è CAP|COMUNE
# - le relazioni sono bidirezionali
# - NON viene applicata transitività
# - ogni località è sempre vicina a se stessa
# - Napoli utilizza una regola speciale
# - la mappa serve SOLO a consigliare le date:
#   non limita mai la possibilità di prenotazione


def _norm_testo(value):
    """Normalizza Comune/località per il confronto."""
    if value is None:
        return ""

    value = str(value).strip().upper()

    # Uniformiamo alcuni caratteri/forme frequenti
    value = value.replace("’", "'")
    value = " ".join(value.split())

    return value


def normalizza_cap(cap):
    """Restituisce il CAP nel formato a 5 cifre."""
    if cap is None:
        return ""

    value = str(cap).strip()

    # Excel può restituire, per esempio, 81030.0
    if value.endswith(".0"):
        value = value[:-2]

    digits = "".join(c for c in value if c.isdigit())

    if not digits:
        return ""

    return digits.zfill(5)


# -------------------------------------------------------------------
# ALIAS COMUNI / LOCALITÀ
# -------------------------------------------------------------------

ALIASES_COMUNI = {
    # Sant'Antimo
    "S.ANTIMO": "SANT'ANTIMO",
    "SANT' ANTIMO": "SANT'ANTIMO",

    # Marano
    "MARANO": "MARANO DI NAPOLI",

    # Mugnano
    "MUGNANO": "MUGNANO DI NAPOLI",

    # Giugliano
    "GIUGLIANO": "GIUGLIANO IN CAMPANIA",

    # Caivano
    "PASCAROLA DI CAIVANO": "CAIVANO",

    # Pozzuoli
    "ARCO FELICE - POZZUOLI": "POZZUOLI",
    "MONTE RUSCELLO POZZUOLI": "POZZUOLI",

    # Sant'Arpino
    "S. ARPINO": "SANT'ARPINO",
    "SANT ARPINO": "SANT'ARPINO",

    # Napoli / località indicate diversamente nel file
    "SECONDIGLIANO": "NAPOLI",
    "S. GIOVANNI - NAPOLI": "NAPOLI",
}


def normalizza_comune(comune):
    comune = _norm_testo(comune)

    return ALIASES_COMUNI.get(comune, comune)


def chiave_zona(cap, comune):
    """
    Crea una chiave territoriale del tipo:
    81030|LUSCIANO
    """
    cap = normalizza_cap(cap)
    comune = normalizza_comune(comune)

    if not cap or not comune:
        return ""

    return f"{cap}|{comune}"


# -------------------------------------------------------------------
# COSTRUZIONE MAPPA
# -------------------------------------------------------------------

VICINANZE = {}


def _aggiungi_zona(zona):
    VICINANZE.setdefault(zona, set()).add(zona)


def _collega(a, b):
    """
    Crea esclusivamente la relazione diretta A <-> B.
    NON genera relazioni transitive.
    """
    _aggiungi_zona(a)
    _aggiungi_zona(b)

    VICINANZE[a].add(b)
    VICINANZE[b].add(a)


def _collega_molti(zona, altre_zone):
    for altra in altre_zone:
        _collega(zona, altra)


# ===================================================================
# GIUGLIANO / MARANO / MUGNANO / QUALIANO / CALVIZZANO / QUARTO
# ===================================================================

_collega_molti(
    "80010|QUARTO",
    {
        "80012|CALVIZZANO",
        "80014|GIUGLIANO IN CAMPANIA",
        "80016|MARANO DI NAPOLI",
        "80018|MUGNANO DI NAPOLI",
        "80019|QUALIANO",
    },
)

# Villaricca condivide 80010 e nelle nostre regole è stata
# considerata nello stesso gruppo operativo Quarto/Villaricca.
_collega_molti(
    "80010|VILLARICCA",
    {
        "80012|CALVIZZANO",
        "80014|GIUGLIANO IN CAMPANIA",
        "80016|MARANO DI NAPOLI",
        "80018|MUGNANO DI NAPOLI",
        "80019|QUALIANO",
    },
)

_collega_molti(
    "80014|GIUGLIANO IN CAMPANIA",
    {
        "80012|CALVIZZANO",
        "80016|MARANO DI NAPOLI",
        "80018|MUGNANO DI NAPOLI",
        "80019|QUALIANO",
    },
)

_collega_molti(
    "80018|MUGNANO DI NAPOLI",
    {
        "80016|MARANO DI NAPOLI",
        "80019|QUALIANO",
        "80012|CALVIZZANO",
    },
)

_collega(
    "80016|MARANO DI NAPOLI",
    "80019|QUALIANO",
)

_collega(
    "80019|QUALIANO",
    "80012|CALVIZZANO",
)

_collega(
    "80012|CALVIZZANO",
    "80016|MARANO DI NAPOLI",
)


# ===================================================================
# FRATTAMAGGIORE / AFRAGOLA / ARZANO / CARDITO / CAIVANO /
# SANT'ANTIMO / CASAVATORE / FRATTAMINORE / CRISPANO
# ===================================================================

# CAP 80020 contiene più comuni.
# Manteniamo i comuni separati ma assegniamo le relazioni che avevamo
# concordato operativamente per il gruppo 80020.

COMUNI_80020 = {
    "80020|CASAVATORE",
    "80020|FRATTAMINORE",
    "80020|CRISPANO",
}

for zona_80020 in COMUNI_80020:

    _collega(
        zona_80020,
        "80022|ARZANO",
    )

    _collega(
        zona_80020,
        "80021|AFRAGOLA",
    )

    _collega(
        zona_80020,
        "80024|CARDITO",
    )

    _collega(
        zona_80020,
        "80027|FRATTAMAGGIORE",
    )

    _collega(
        zona_80020,
        "80029|SANT'ANTIMO",
    )

    _collega(
        zona_80020,
        "80023|CAIVANO",
    )


_collega(
    "80021|AFRAGOLA",
    "80024|CARDITO",
)

_collega_molti(
    "80027|FRATTAMAGGIORE",
    {
        "80021|AFRAGOLA",
        "80022|ARZANO",
        "80024|CARDITO",
        "80029|SANT'ANTIMO",
        "80023|CAIVANO",
    },
)

_collega_molti(
    "80029|SANT'ANTIMO",
    {
        "80018|MUGNANO DI NAPOLI",
        "80022|ARZANO",
        "80024|CARDITO",
    },
)

_collega_molti(
    "80024|CARDITO",
    {
        "80021|AFRAGOLA",
        "80022|ARZANO",
        "80023|CAIVANO",
    },
)

_collega(
    "80022|ARZANO",
    "80021|AFRAGOLA",
)

_collega(
    "80021|AFRAGOLA",
    "80023|CAIVANO",
)


# ===================================================================
# CASANDRINO / GRUMO NEVANO
# ===================================================================

_collega_molti(
    "80025|CASANDRINO",
    {
        "80029|SANT'ANTIMO",
        "80028|GRUMO NEVANO",
    },
)

_collega_molti(
    "80028|GRUMO NEVANO",
    {
        "80027|FRATTAMAGGIORE",
        "80024|CARDITO",
        "80029|SANT'ANTIMO",
        "80020|FRATTAMINORE",
        "80020|CRISPANO",
    },
)


# ===================================================================
# MELITO
# ===================================================================

_collega_molti(
    "80017|MELITO DI NAPOLI",
    {
        "80018|MUGNANO DI NAPOLI",
        "80029|SANT'ANTIMO",
        "80016|MARANO DI NAPOLI",
        "80022|ARZANO",
    },
)


# ===================================================================
# AREA FLEGREA
# ===================================================================

_collega(
    "80070|BACOLI",
    "80078|POZZUOLI",
)

_collega(
    "80070|MONTE DI PROCIDA",
    "80078|POZZUOLI",
)


# ===================================================================
# NAPOLI
# ===================================================================

# Tutte le farmacie identificate come Comune = NAPOLI vengono
# considerate tra loro vicine automaticamente.
#
# Manteniamo qui soltanto le relazioni EXTRA-NAPOLI esplicitamente
# concordate.

_collega_molti(
    "80145|NAPOLI",
    {
        "80022|ARZANO",
        "80020|CASAVATORE",
        "80020|FRATTAMINORE",
        "80020|CRISPANO",
        "80021|AFRAGOLA",
    },
)

_collega_molti(
    "80144|NAPOLI",
    {
        "80022|ARZANO",
        "80020|CASAVATORE",
        "80020|FRATTAMINORE",
        "80020|CRISPANO",
    },
)


# ===================================================================
# NOLA / CASALNUOVO / ACERRA
# ===================================================================

_collega_molti(
    "80035|NOLA",
    {
        "80013|CASALNUOVO DI NAPOLI",
        "80011|ACERRA",
    },
)

_collega_molti(
    "80013|CASALNUOVO DI NAPOLI",
    {
        "80021|AFRAGOLA",
        "80023|CAIVANO",
        "80011|ACERRA",
    },
)

_collega_molti(
    "80011|ACERRA",
    {
        "80021|AFRAGOLA",
        "80023|CAIVANO",
        "80024|CARDITO",
    },
)


# ===================================================================
# CASTELLO DI CISTERNA / POMIGLIANO
# ===================================================================

_collega_molti(
    "80030|CASTELLO DI CISTERNA",
    {
        "80038|POMIGLIANO D'ARCO",
        "80013|CASALNUOVO DI NAPOLI",
        "80011|ACERRA",
        "80035|NOLA",
    },
)

_collega_molti(
    "80038|POMIGLIANO D'ARCO",
    {
        "80011|ACERRA",
        "80013|CASALNUOVO DI NAPOLI",
        "80035|NOLA",
    },
)


# ===================================================================
# AVERSA / AGRO AVERSANO
# ===================================================================

_collega(
    "81031|AVERSA",
    "81030|GRICIGNANO DI AVERSA",
)

_collega(
    "81031|AVERSA",
    "81030|LUSCIANO",
)

_collega(
    "81031|AVERSA",
    "81030|PARETE",
)

_collega(
    "81031|AVERSA",
    "81030|SUCCIVO",
)

_collega(
    "81031|AVERSA",
    "81030|TEVEROLA",
)

_collega(
    "81031|AVERSA",
    "81030|SANT'ARPINO",
)


# Lusciano

_collega_molti(
    "81030|LUSCIANO",
    {
        "81030|PARETE",
        "81030|GRICIGNANO DI AVERSA",
        "81030|SUCCIVO",
        "81030|TEVEROLA",
        "81030|SANT'ARPINO",
    },
)


# Parete

_collega_molti(
    "81030|PARETE",
    {
        "81030|GRICIGNANO DI AVERSA",
        "81030|SUCCIVO",
        "81030|TEVEROLA",
        "81030|SANT'ARPINO",
    },
)


# Gricignano

_collega_molti(
    "81030|GRICIGNANO DI AVERSA",
    {
        "81030|SUCCIVO",
        "81030|TEVEROLA",
        "81030|SANT'ARPINO",
    },
)


# Succivo

_collega_molti(
    "81030|SUCCIVO",
    {
        "81030|TEVEROLA",
        "81030|SANT'ARPINO",
    },
)


# Teverola

_collega(
    "81030|TEVEROLA",
    "81030|SANT'ARPINO",
)


# ===================================================================
# CASTEL VOLTURNO / CELLOLE / BAIA DOMIZIA
# ===================================================================

_collega(
    "81030|CASTEL VOLTURNO",
    "81037|BAIA DOMIZIA",
)

_collega(
    "81030|CASTEL VOLTURNO",
    "81030|CELLOLE",
)

_collega(
    "81030|CELLOLE",
    "81037|BAIA DOMIZIA",
)


# ===================================================================
# CAPODRISE / SAN MARCO EVANGELISTA / CASERTA / AVERSA
# ===================================================================

_collega_molti(
    "81020|CAPODRISE",
    {
        "81020|SAN MARCO EVANGELISTA",
        "81100|CASERTA",
        "81031|AVERSA",
    },
)

_collega_molti(
    "81100|CASERTA",
    {
        "81020|SAN MARCO EVANGELISTA",
        "81031|AVERSA",
    },
)

_collega(
    "81020|SAN MARCO EVANGELISTA",
    "81031|AVERSA",
)


# ===================================================================
# COMUNI ISOLATI
# ===================================================================

# Questi comuni non ricevono collegamenti con altri comuni.
# Rimangono comunque vicini a se stessi.

_aggiungi_zona(
    "82010|MOIANO"
)

_aggiungi_zona(
    "84087|SARNO"
)


# ===================================================================
# RELAZIONI ESPLICITAMENTE ESCLUSE
# ===================================================================
#
# Non sono strettamente necessarie per il funzionamento perché
# l'assenza da VICINANZE equivale già a "non vicino".
#
# Le conserviamo però per documentare le decisioni prese e impedire
# che future modifiche automatiche le introducano accidentalmente.

NON_VICINI = {
    frozenset({
        "80020|CASAVATORE",
        "80018|MUGNANO DI NAPOLI",
    }),

    frozenset({
        "80020|FRATTAMINORE",
        "80018|MUGNANO DI NAPOLI",
    }),

    frozenset({
        "80020|CRISPANO",
        "80018|MUGNANO DI NAPOLI",
    }),

    frozenset({
        "80025|CASANDRINO",
        "80018|MUGNANO DI NAPOLI",
    }),

    frozenset({
        "80025|CASANDRINO",
        "80012|CALVIZZANO",
    }),

    frozenset({
        "80078|POZZUOLI",
        "80010|QUARTO",
    }),

    frozenset({
        "80078|POZZUOLI",
        "80010|VILLARICCA",
    }),

    frozenset({
        "81030|CASTEL VOLTURNO",
        "81030|PARETE",
    }),

    frozenset({
        "81030|CASTEL VOLTURNO",
        "81030|LUSCIANO",
    }),
}


# ===================================================================
# FUNZIONI UTILIZZATE DA APP.PY
# ===================================================================

def sono_napoli(zona):
    """
    Verifica se una chiave CAP|Comune appartiene al Comune di Napoli.
    """
    if not zona:
        return False

    try:
        _, comune = zona.split("|", 1)
    except ValueError:
        return False

    return normalizza_comune(comune) == "NAPOLI"


def sono_vicini(cap1, comune1, cap2, comune2):
    """
    Restituisce True esclusivamente se due zone sono considerate vicine.

    Nessuna transitività viene applicata.
    """

    zona1 = chiave_zona(cap1, comune1)
    zona2 = chiave_zona(cap2, comune2)

    if not zona1 or not zona2:
        return False

    # Stessa identica zona
    if zona1 == zona2:
        return True

    # Regola globale Napoli:
    # tutti i CAP del Comune di Napoli sono reciprocamente vicini.
    if sono_napoli(zona1) and sono_napoli(zona2):
        return True

    # Eventuale esclusione esplicita
    coppia = frozenset({zona1, zona2})

    if coppia in NON_VICINI:
        return False

    # Solo relazione diretta
    return zona2 in VICINANZE.get(zona1, set())


def zone_vicine(cap, comune):
    """
    Restituisce l'insieme delle zone direttamente vicine.

    Per Napoli aggiunge dinamicamente le altre zone Napoli che
    risultano già presenti nella mappa.

    NOTA:
    app.py potrà inoltre confrontare direttamente le farmacie
    attraverso sono_vicini(), quindi non è necessario avere tutti
    i CAP di Napoli scritti manualmente qui.
    """

    zona = chiave_zona(cap, comune)

    if not zona:
        return set()

    risultato = set(
        VICINANZE.get(zona, set())
    )

    risultato.add(zona)

    if sono_napoli(zona):
        for altra_zona in VICINANZE:
            if sono_napoli(altra_zona):
                risultato.add(altra_zona)

    return risultato
