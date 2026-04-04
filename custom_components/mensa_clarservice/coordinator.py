"""Coordinatore aggiornamento dati per Mensa ClarService."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MensaClient, MensaApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MensaClarServiceCoordinator(DataUpdateCoordinator):
    """Coordinatore per recuperare dati dalla mensa."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MensaClient,
        scan_interval: int,
    ) -> None:
        """Inizializza il coordinatore."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Recupera i dati dalla mensa."""
        try:
            return await self.client.fetch_all_data()
        except MensaApiError as err:
            raise UpdateFailed(f"Errore aggiornamento dati mensa: {err}") from err
