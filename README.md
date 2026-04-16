# Mensa ClarService per Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=yashijoe&repository=ha-mensa-clarservice&category=integration)

Integrazione custom per Home Assistant che recupera il menu della mensa dal portale **ClarService** (clarservice.com).

## Funzionalità

- **Menu del giorno** — primo, secondo e contorno ordinati per oggi
- **Menu dei prossimi 5 giorni lavorativi** — con nomi dinamici (domani, lunedì, martedì, ecc.)
- **Gestione festività italiane** — salta automaticamente weekend e festivi (inclusa Pasquetta)
- **Aggiornamento configurabile** — intervallo di polling personalizzabile (default: 30 minuti)
- **Configurazione da UI** — nessun YAML necessario

## Requisiti

- Home Assistant 2024.1.0 o superiore
- Un account attivo su [clarservice.com](https://www.clarservice.com)

## Installazione

### HACS (consigliato)

1. Apri HACS in Home Assistant
2. Vai su **Integrazioni**
3. Menu tre puntini (in alto a destra) → **Repository personalizzati**
4. Aggiungi `https://github.com/yashijoe/ha-mensa-clarservice` come **Integrazione**
5. Cerca "Mensa ClarService" e installa
6. Riavvia Home Assistant

### Manuale

1. Scarica l'ultima release da GitHub
2. Copia la cartella `custom_components/mensa_clarservice` nella cartella `config/custom_components/` di HA
3. Riavvia Home Assistant

## Configurazione

1. Vai su **Impostazioni** → **Dispositivi e servizi** → **Aggiungi integrazione**
2. Cerca **Mensa ClarService**
3. Inserisci:
   - **Email**: la tua email di accesso a ClarService
   - **Password**: la tua password
   - **Intervallo di aggiornamento**: frequenza di polling in minuti (default: 30, range: 5–120)
4. Clicca **Invia**

### Opzioni (post-configurazione)

Vai su **Impostazioni** → **Dispositivi e servizi** → **Mensa ClarService** → **Configura** per modificare l'intervallo di aggiornamento.

## Sensori

### Oggi

| Entità | Alias | Icona |
|--------|-------|-------|
| `sensor.mensa_primo` | Primo | 🍝 |
| `sensor.mensa_secondo` | Secondo | 🍗 |
| `sensor.mensa_contorno` | Contorno | 🍎 |

### Prossimi giorni lavorativi

| Entità | Alias (esempio) | Note |
|--------|-----------------|------|
| `sensor.mensa_plus1_primo` | Primo domani | Se il giorno successivo è lavorativo |
| `sensor.mensa_plus1_primo` | Primo lunedì | Se il giorno successivo non è domani |
| `sensor.mensa_plus2_primo` | Primo martedì | |
| `sensor.mensa_plus3_primo` | Primo mercoledì | |
| `sensor.mensa_plus4_primo` | Primo giovedì | |
| `sensor.mensa_plus5_primo` | Primo venerdì | |

Lo stesso pattern si applica a `_secondo` e `_contorno`.

### Attributi

Ogni sensore include:

- `data` — data del giorno in formato ISO (es. `2026-04-07`)
- `giorno` — nome del giorno della settimana (es. `lunedì`)
- `codice_piatto` — codice numerico del piatto (es. `3`)

### Stato

- Il nome del piatto (es. `PASTICCIO DI POLENTA`)
- `Nessun piatto` — se non ci sono ordinazioni per quel giorno

## Dashboard (esempio)

```yaml
type: entities
title: 🍽️ Menu di oggi
entities:
  - entity: sensor.mensa_primo
  - entity: sensor.mensa_secondo
  - entity: sensor.mensa_contorno
```

```yaml
type: entities
title: 🍽️ Menu domani
entities:
  - entity: sensor.mensa_plus1_primo
  - entity: sensor.mensa_plus1_secondo
  - entity: sensor.mensa_plus1_contorno
```

## Gestione festività

L'integrazione gestisce automaticamente le festività italiane:

- **Fisse**: Capodanno, Epifania, 25 aprile, 1 maggio, 2 giugno, Ferragosto, Ognissanti, Immacolata, Natale, Santo Stefano
- **Mobili**: Pasquetta (calcolata automaticamente)
- **Weekend**: sabato e domenica esclusi

Se oggi è venerdì, `sensor.mensa_plus1_primo` mostrerà il menu di lunedì (saltando il weekend).

## Risoluzione problemi

**"Credenziali non valide"** — Verifica email e password su [clarservice.com](https://www.clarservice.com/utilizzatore/index.php).

**"Nessun piatto"** — Nessuna ordinazione trovata per quel giorno. Può significare che il menu non è ancora stato caricato o che non hai ordinato.

**Sensori non aggiornati** — Controlla l'intervallo di aggiornamento nelle opzioni dell'integrazione.

## Licenza

Questo progetto è rilasciato sotto licenza MIT — vedi il file [LICENSE](LICENSE) per i dettagli.
