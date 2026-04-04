"""Config flow per Mensa ClarService."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import MensaClient, MensaAuthError, MensaApiError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class MensaClarServiceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Gestione config flow per Mensa ClarService."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestione step iniziale."""
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            client = MensaClient(username, password)
            try:
                await client.test_connection()
            except MensaAuthError:
                errors["base"] = "invalid_auth"
            except MensaApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Errore imprevisto")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"mensa_clarservice_{username}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Mensa ({username})",
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                    options={
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=5, max=120)),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Restituisce il flow delle opzioni."""
        return MensaClarServiceOptionsFlow(config_entry)


class MensaClarServiceOptionsFlow(OptionsFlow):
    """Gestione opzioni per Mensa ClarService."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Inizializza."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestione opzioni."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(int, vol.Range(min=5, max=120)),
                }
            ),
        )
