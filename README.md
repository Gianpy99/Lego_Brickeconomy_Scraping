# LEGO LEGO Collection Manager con BrickEconomy Integration

Un'applicazione web per gestire la collezione LEGO, con interfaccia REST API e pagine statiche responsive, integrata con dati di BrickEconomy.

## Features

- **Professional Architecture**: Modular design with proper separation of concerns
- **Robust Error Handling**: Comprehensive exception handling and logging
- **Multiple Input Formats**: Support for Excel, CSV, text files, and direct input
- **Multiple Output Formats**: Excel, CSV, JSON export with summary reports
- **Configurable**: Environment-based configuration with validation
- **Automatic Driver Management**: Uses webdriver-manager for ChromeDriver
- **Rate Limiting**: Configurable delays between requests
- **Data Validation**: Clean and validate scraped data
- **Comprehensive Logging**: Detailed logging with multiple levels

## Struttura del Progetto

- main.py                   : punto di ingresso, server HTTP e API REST
- config.py                 : gestione configurazione da file .env
- database_manager.py       : operazioni sul database SQLite (backup, query, validazione)
- lego_database.py          : scraper per informazioni sui set LEGO
- minifig_database.py       : scraper per informazioni sulle minifigure
- enhanced_web_generator.py : generazione delle pagine web responsive
- analyze_matrix.py         : generazione vista matrice relazioni
- populate_connections.py   : popolamento connessioni set-minifigure
- check_db.py               : controlli di integrità del database
- models.py                 : definizione dei modelli dati
- logging_system.py         : configurazione del logging
- exceptions.py             : eccezioni personalizzate
- system_test.py            : test di sistema end-to-end
- requirements.txt          : dipendenze Python
- .env.example              : template file di configurazione

### Cartelle principali
- lego_database/            : pagine web statiche e database
  - index.html               : dashboard principale
  - sets.html                : elenco set LEGO
  - minifigs.html            : elenco minifigure
  - analytics.html           : dashboard analytics
  - matrix.html              : vista matrice relazioni
  - LegoDatabase.db          : database SQLite
  - images/                  : immagini dei set e minifigure
  - backups/                 : backup automatici del database
- logs/                     : file di log generati

## Installazione

1. Clona il repository:
   ```powershell
   git clone https://github.com/Gianpy99/Lego_Brickeconomy_Scraping.git
   cd Lego_Brickeconomy_Scraping
   ```
2. Crea e attiva un ambiente virtuale Python:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
3. Installa le dipendenze:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copia il file `.env.example` in `.env` e configura i parametri se necessario.

### Manual Setup

1. **Create Python 3.13 virtual environment:**
```bash
py -3.13 -m venv venv_py313
```

2. **Activate the environment:**
```bash
# Windows
.\activate_env.bat

# PowerShell
.\activate_env.ps1

# Manual activation
.\venv_py313\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure credentials:**
Copy `.env.example` to `.env` and edit with your BrickEconomy credentials:
```
BRICKECONOMY_USERNAME=your_username
BRICKECONOMY_PASSWORD=your_password
```

## Avvio dell'Applicazione

Esegui il server HTTP e le API:
```powershell
python main.py
```
Apri il browser su http://localhost:8000 per accedere alla dashboard principale.

## Funzionalità Principali

- **API REST**:
  - `/api/sets`        : restituisce lista di set
  - `/api/minifigs`    : restituisce lista di minifigure
  - `/api/matrix-data`: dati per la vista matrice
  - `/api/set/{id}`    : dettagli di un set
  - `/api/minifig/{id}`: dettagli di una minifigure
- **Pagine Web Statiche**:
  - `index.html`   : dashboard con statistiche e grafici
  - `sets.html`    : elenco e dettagli dei set
  - `minifigs.html`: elenco e dettagli delle minifigure
  - `analytics.html`: analisi avanzata con Chart.js
  - `matrix.html`  : matrice relazioni set-minifigura

### Interactive Demonstration

```bash
# Run the interactive demo
python demo.py
```

### Python API

```python
from scraper import BrickEconomyScraper
from data_loader import DataLoader
from data_export import DataExporter

# Load codes
codes = DataLoader.load_from_excel("input.xlsx", "Set Code")

# Scrape data
with BrickEconomyScraper() as scraper:
    results = scraper.scrape_lego_sets(codes)

# Export results
exporter = DataExporter()
exporter.to_excel(results)
```

## Configurazione

Modifica `config.py` o `.env` per personalizzare:
- `SCRAPING_DELAY`     : intervallo tra le richieste di scraping
- `HEADLESS`           : modalità headless per Selenium
- `OUTPUT_DIRECTORY`   : directory di output per dati ed export

## Output Data

The scraper extracts the following information for each LEGO set:

- Official name
- Number of pieces
- Number of minifigures
- Release date
- Retirement date
- Current market value (new sealed)
- Current market value (used)
- Value range
- Retail prices (EUR/GBP)

## Error Handling

The scraper includes comprehensive error handling for:

- Network connectivity issues
- Element not found errors
- Login failures
- Data validation errors
- Rate limiting and timeouts

## Logging

Detailed logging is available at multiple levels:
- INFO: General progress information
- DEBUG: Detailed debugging information
- ERROR: Error messages with stack traces
- WARNING: Non-critical issues

## Licenza

Progetto per scopi educativi. Rispetta i termini di servizio di BrickEconomy e utilizza un rate limiting adeguato.