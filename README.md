# Property24 Kenya – Asynchronous Web Scraper

An asynchronous Python web-scraping project designed to collect property listing information from [Property24 Kenya](https://www.property24.co.ke/).

The scraper extracts property details across multiple listing pages, processes the HTML using BeautifulSoup, removes duplicate listings, and exports the collected information into a structured CSV dataset.

## Project Overview

This project demonstrates practical applications of Python web scraping, asynchronous programming, HTML parsing, data processing, and CSV automation.

It targets Property24's Nairobi property-for-sale listings and collects information from multiple paginated results.

### Features

- **Asynchronous scraping:** Uses `asyncio` and `aiohttp` to make concurrent HTTP requests.
- **Pagination handling:** Scrapes property listings across multiple pages.
- **HTML parsing:** Uses BeautifulSoup and CSS selectors to extract listing information.
- **Property data extraction:** Collects titles, prices, locations, property URLs, and image URLs.
- **Duplicate removal:** Uses property URLs to identify and remove duplicate records.
- **CSV export:** Saves extracted records into a structured CSV file.
- **Request management:** Uses configurable concurrency, request delays, and HTTP timeouts.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| asyncio | Asynchronous task management |
| aiohttp | Asynchronous HTTP requests |
| BeautifulSoup4 | HTML parsing and data extraction |
| pandas | Data manipulation and CSV export |
| Git & GitHub | Version control and project hosting |

## Project Structure

```text
Property24AfricaDataListing/
│
├── property24_async_scraper.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── Property24Africa_all_pages.csv
```

The CSV file is generated when the scraper runs. It may be excluded from GitHub through `.gitignore`.

## Data Collected

The scraper extracts the following information:

| Field | Description |
|---|---|
| Title | Property listing title |
| Price | Advertised property price |
| Location | Property location |
| PropertyUrl | Direct URL to the listing |
| Image_url | Property image URL |

### Example Output

| Title | Price | Location |
|---|---|---|
| 2 Bedroom Apartment / Flat | KSh 12 500 000 | Westlands |
| 3 Bedroom Apartment / Flat | Listing price | Nairobi |

*Illustrative example of the extracted data.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Property24AfricaDataListing.git
```

Navigate into the project:

```bash
cd Property24AfricaDataListing
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the dependencies manually:

```bash
pip install aiohttp beautifulsoup4 pandas
```

## Running the Scraper

Run the Python script:

```bash
python property24_async_scraper.py
```

The scraper will request the configured listing pages, extract property information, remove duplicate property URLs, and export the results to:

```text
Property24Africa_all_pages.csv
```

## How It Works

The scraping workflow follows these stages:

1. **Initialize:** Configure the target URL, HTTP headers, and request settings.
2. **Request:** Fetch listing pages asynchronously using aiohttp.
3. **Parse:** Convert HTML responses into BeautifulSoup objects.
4. **Extract:** Locate property information using CSS selectors.
5. **Process:** Organize the extracted records into Python data structures.
6. **Deduplicate:** Remove repeated listings using their property URLs.
7. **Export:** Convert the final records into a CSV dataset using pandas.

## Future Improvements

Potential improvements for future versions include:

- Automatic pagination detection.
- Retry handling for temporary HTTP errors.
- Incremental CSV saving and recovery after interruptions.
- Improved logging and error reporting.
- Data validation and normalization.
- Extraction of additional property attributes.
- Database integration using SQLite or PostgreSQL.
- Scheduling automated scraping jobs.

## Responsible Scraping

This project is intended for educational and research purposes.

Before running the scraper, review Property24's applicable terms of service, robots.txt, and access restrictions. Keep request rates reasonable, respect rate limits, and do not attempt to bypass access controls or anti-bot protections.

Only collect and use data in ways permitted by the website and applicable laws.

## Author

**Property24AfricaDataListing**

Python | Web Scraping | Asynchronous Programming | Data Extraction | CSV Automation

---

*This project is part of a practical journey into Python automation, web scraping, and data engineering.*
