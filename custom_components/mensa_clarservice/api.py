"""Client API per Mensa ClarService."""

import logging
import re
from datetime import date, timedelta

import aiohttp

from .const import BASE_URL, FESTIVITA_FISSE

_LOGGER = logging.getLogger(__name__)


def _calcola_pasqua(anno: int) -> date:
    """Calcola la data di Pasqua con l'algoritmo di Gauss."""
    a = anno % 19
    b = anno // 100
    c = anno % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mese = (h + l - 7 * m + 114) // 31
    giorno = ((h + l - 7 * m + 114) % 31) + 1
    return date(anno, mese, giorno)


def _festivita_mobili(anno: int) -> list[date]:
    """Calcola Pasquetta."""
    pasqua = _calcola_pasqua(anno)
    return [pasqua + timedelta(days=1)]  # Lunedì dell'Angelo


def e_festivo(giorno: date) -> bool:
    """Verifica se un giorno è festivo in Italia."""
    # Weekend
    if giorno.weekday() >= 5:
        return True
    # Festività fisse
    if (giorno.month, giorno.day) in FESTIVITA_FISSE:
        return True
    # Festività mobili
    if giorno in _festivita_mobili(giorno.year):
        return True
    return False


def e_giorno_lavorativo(giorno: date) -> bool:
    """Verifica se è un giorno lavorativo (lun-ven, no festivi)."""
    return not e_festivo(giorno)


def prossimi_giorni_lavorativi(da: date, quanti: int) -> list[date]:
    """Restituisce i prossimi N giorni lavorativi a partire dal giorno dopo 'da'."""
    risultato = []
    giorno = da + timedelta(days=1)
    while len(risultato) < quanti:
        if e_giorno_lavorativo(giorno):
            risultato.append(giorno)
        giorno += timedelta(days=1)
    return risultato


def _parse_piatti(html: str) -> list[str]:
    """Estrai i piatti dall'HTML."""
    if "Non ci sono ordinazioni" in html:
        return []

    righe = re.findall(
        r"<tr.*?>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>(.*?)</td>",
        html,
        re.DOTALL,
    )

    piatti = []
    for campo in righe:
        campo = re.sub("<[^>]*>", "", campo).strip()
        parti = campo.split("|")
        if len(parti) >= 2:
            codice = parti[0].strip()
            nome = parti[1].strip().lstrip("*")
            piatti.append(f"{nome} ({codice})")

    return piatti


class MensaApiError(Exception):
    """Errore API generico."""


class MensaAuthError(MensaApiError):
    """Errore di autenticazione."""


class MensaClient:
    """Client per interagire con ClarService."""

    def __init__(self, username: str, password: str) -> None:
        """Inizializza il client."""
        self._username = username
        self._password = password

    async def test_connection(self) -> bool:
        """Testa la connessione."""
        async with aiohttp.ClientSession() as session:
            await self._login(session)
            return True

    async def _login(self, session: aiohttp.ClientSession) -> None:
        """Esegui login."""
        login_data = {
            "mail_admin": self._username,
            "pass_admin": self._password,
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with session.post(
                BASE_URL, data=login_data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                text = await resp.text()
                if "login" in text.lower() and "errore" in text.lower():
                    raise MensaAuthError("Credenziali non valide")
        except aiohttp.ClientError as err:
            raise MensaApiError(f"Errore di connessione: {err}") from err

    async def fetch_menu(self, giorno: date) -> list[str]:
        """Recupera il menu per un giorno specifico."""
        async with aiohttp.ClientSession() as session:
            await self._login(session)
            return await self._get_ordini(session, giorno)

    async def _get_ordini(self, session: aiohttp.ClientSession, giorno: date) -> list[str]:
        """Recupera gli ordini per una data."""
        data_str = giorno.strftime("%Y-%m-%d")
        url = f"{BASE_URL}?azione=visualizzaOrdiniGiorno&data_ordinazione={data_str}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
                return _parse_piatti(html)
        except aiohttp.ClientError as err:
            raise MensaApiError(f"Errore recupero menu: {err}") from err

    async def fetch_all_data(self) -> dict[str, list[str]]:
        """Recupera menu di oggi e dei prossimi 4 giorni lavorativi."""
        oggi = date.today()
        giorni_futuri = prossimi_giorni_lavorativi(oggi, 4)

        async with aiohttp.ClientSession() as session:
            await self._login(session)

            data = {}

            # Oggi (solo se lavorativo)
            if e_giorno_lavorativo(oggi):
                try:
                    data["oggi"] = {
                        "piatti": await self._get_ordini(session, oggi),
                        "data": oggi,
                    }
                except MensaApiError as err:
                    _LOGGER.warning("Errore recupero menu oggi: %s", err)
                    data["oggi"] = {"piatti": [], "data": oggi}
            else:
                data["oggi"] = {"piatti": [], "data": oggi}

            # Prossimi giorni lavorativi
            for i, giorno in enumerate(giorni_futuri):
                key = f"plus{i + 1}"
                try:
                    data[key] = {
                        "piatti": await self._get_ordini(session, giorno),
                        "data": giorno,
                    }
                except MensaApiError as err:
                    _LOGGER.warning("Errore recupero menu %s: %s", giorno, err)
                    data[key] = {"piatti": [], "data": giorno}

            return data
