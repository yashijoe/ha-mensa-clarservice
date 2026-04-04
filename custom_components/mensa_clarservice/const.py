"""Costanti per l'integrazione Mensa ClarService."""

DOMAIN = "mensa_clarservice"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30  # minuti

BASE_URL = "https://www.clarservice.com/utilizzatore/index.php"

# Festività italiane fisse
FESTIVITA_FISSE = [
    (1, 1),    # Capodanno
    (1, 6),    # Epifania
    (4, 25),   # Liberazione
    (5, 1),    # Festa del lavoro
    (6, 2),    # Festa della Repubblica
    (8, 15),   # Ferragosto
    (11, 1),   # Ognissanti
    (12, 8),   # Immacolata
    (12, 25),  # Natale
    (12, 26),  # Santo Stefano
]

GIORNI_SETTIMANA = {
    0: "lunedì",
    1: "martedì",
    2: "mercoledì",
    3: "giovedì",
    4: "venerdì",
    5: "sabato",
    6: "domenica",
}

PIATTI = [
    {"key": "primo", "name": "Primo", "icon": "mdi:pasta"},
    {"key": "secondo", "name": "Secondo", "icon": "mdi:food-turkey"},
    {"key": "contorno", "name": "Contorno", "icon": "mdi:apple"},
]
