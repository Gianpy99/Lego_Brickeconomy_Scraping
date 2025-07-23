# LEGO BrickEconomy Professional Scraper

A professional web scraper for extracting LEGO set information from BrickEconomy.com with robust error handling, modular design, and comprehensive data export capabilities.

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

## Project Structure

```
├── main.py              # Command-line interface
├── demo.py              # Interactive demonstration
├── scraper.py           # Core scraping functionality
├── config.py            # Configuration management
├── models.py            # Data models
├── data_loader.py       # Input data handling
├── data_export.py       # Output data handling
├── exceptions.py        # Custom exceptions
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── setup.py             # Setup script
```

## Installation

### Quick Setup (Recommended)

1. **Run the quick setup script:**
```bash
python quick_start.py
```
This will automatically:
- Check Python 3.13 availability
- Create virtual environment
- Install all dependencies
- Create .env file template

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

## Usage

### Quick Start

```bash
# Run interactive demonstration
python demo.py

# Quick test
python main.py --codes "3920"
```

### Command Line Interface

```bash
# Scrape specific LEGO codes
python main.py --codes "3920,9469,10333"

# From Excel file
python main.py --excel-file "input.xlsx" --column "Set Code"

# From CSV file
python main.py --csv-file "codes.csv" --output-format json

# From text file with custom options
python main.py --text-file "codes.txt" --headless --verbose --delay 3
```

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

## Configuration

Key configuration options in `config.py`:

- `TARGET_THEMES`: LEGO themes to include in scraping
- `WAIT_TIME`: Selenium wait timeout
- `SCRAPING_DELAY`: Delay between requests
- `HEADLESS`: Run browser in headless mode
- `OUTPUT_DIRECTORY`: Directory for output files

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

## License

This project is for educational purposes only. Please respect BrickEconomy's terms of service and implement appropriate rate limiting.