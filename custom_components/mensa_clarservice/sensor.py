"""Piattaforma sensori per Mensa ClarService."""

import logging
from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PIATTI, GIORNI_SETTIMANA
from .coordinator import MensaClarServiceCoordinator
from .api import e_giorno_lavorativo, prossimi_giorni_lavorativi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura i sensori dalla config entry."""
    coordinator: MensaClarServiceCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Sensori di oggi
    for piatto in PIATTI:
        entities.append(
            MensaSensor(coordinator, entry, "oggi", piatto, 0)
        )

    # Sensori prossimi 5 giorni lavorativi
    for offset in range(1, 6):
        for piatto in PIATTI:
            entities.append(
                MensaSensor(coordinator, entry, f"plus{offset}", piatto, offset)
            )

    async_add_entities(entities)


class MensaSensor(CoordinatorEntity, SensorEntity):
    """Sensore per un piatto della mensa."""

    def __init__(
        self,
        coordinator: MensaClarServiceCoordinator,
        entry: ConfigEntry,
        data_key: str,
        piatto: dict,
        offset: int,
    ) -> None:
        """Inizializza."""
        super().__init__(coordinator)
        self._entry = entry
        self._data_key = data_key
        self._piatto = piatto
        self._offset = offset
        self._piatto_index = {"primo": 0, "secondo": 1, "contorno": 2}[piatto["key"]]

        # Entity ID fisso
        if offset == 0:
            self.entity_id = f"sensor.mensa_{piatto['key']}"
        else:
            self.entity_id = f"sensor.mensa_plus{offset}_{piatto['key']}"

        self._attr_unique_id = f"{entry.entry_id}_{data_key}_{piatto['key']}"
        self._attr_icon = piatto["icon"]

    def _get_target_date(self) -> date | None:
        """Ottieni la data target per questo sensore."""
        day_data = self.coordinator.data.get(self._data_key, {})
        return day_data.get("data")

    def _get_day_label(self) -> str:
        """Ottieni l'etichetta del giorno."""
        oggi = date.today()
        target = self._get_target_date()
        if not target:
            return self._piatto["name"]

        delta = (target - oggi).days
        if delta == 0:
            return self._piatto["name"]
        elif delta == 1:
            return f"{self._piatto['name']} domani"
        else:
            giorno_nome = GIORNI_SETTIMANA.get(target.weekday(), str(target))
            return f"{self._piatto['name']} {giorno_nome}"

    @property
    def name(self) -> str:
        """Nome dinamico del sensore."""
        return self._get_day_label()

    @property
    def native_value(self) -> str:
        """Stato del sensore."""
        day_data = self.coordinator.data.get(self._data_key, {})
        piatti = day_data.get("piatti", [])
        if self._piatto_index < len(piatti):
            return piatti[self._piatto_index]
        return "Nessun piatto"

    @property
    def extra_state_attributes(self) -> dict:
        """Attributi extra."""
        target = self._get_target_date()
        attrs = {}
        if target:
            attrs["data"] = target.isoformat()
            attrs["giorno"] = GIORNI_SETTIMANA.get(target.weekday(), "")
        return attrs

    @property
    def device_info(self):
        """Info dispositivo."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Mensa",
            "manufacturer": "ClarService",
            "configuration_url": "https://www.clarservice.com",
        }
