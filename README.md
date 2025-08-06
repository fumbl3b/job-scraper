# Job Scraper

This repository contains a simple, extensible Python tool for scraping recent job listings from public job boards.  
The goal of this tool is to provide an easy way to discover recently posted jobs based on keywords and location.  
The core of the tool is a command‑line interface that queries a supported job site and returns a list of matching postings.

## ⚠️ Ethical considerations and terms of service

Before using this tool against any job board you **must** familiarise yourself with that board’s terms of service.  
Many sites – including LinkedIn and Indeed – prohibit automated scraping or require an API key.  
This repository is meant as an educational starting point; it does **not** encourage violating any website’s policies.  
The only site currently supported out‑of‑the‑box is **The Muse**, which exposes a public JSON API.  
Support for additional sites can be added by implementing new scraper classes that respect each site’s rules and rate limits.

## Features

- Query recently posted jobs using one or more keywords.
- Filter results by location and the maximum age (in days) of the listing.
- Export results to the console, JSON or CSV files.
- Modular design allows new job boards to be added without changing the CLI.

## Quick start

1. Clone this repository (or use it via the provided GitHub repository).
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the scraper.  For example, to search The Muse for “software engineer” roles in Philadelphia posted in the last 7 days and display the first 30 matches:

   ```bash
   python cli.py \
       --site themuse \
       --query "software engineer" \
       --location "Philadelphia, PA" \
       --days 7 \
       --max-results 30
   ```

This will print a table of results to the console.  To write results to a file instead, supply `--output /path/to/file.json` or a `.csv` file.  The format is automatically inferred from the extension.

## Architecture

The scraper is composed of two parts:

1. A **CLI** (`cli.py`) that parses command‑line arguments, instantiates the appropriate site scraper and orchestrates the retrieval and output of results.
2. **Scraper classes** (`job_scraper/scrapers/*.py`) that know how to talk to a particular job board.  Each scraper must implement a `search()` method that takes a query, location, days limit and maximum number of results and returns a list of job dictionaries.

Currently only the `TheMuseScraper` is fully implemented.  Stubs exist for Indeed and LinkedIn for future expansion.

### Adding a new site

To add support for another job site:

1. Create a new file in `job_scraper/scrapers/` (for example `my_site_scraper.py`).
2. Implement a class that inherits from `BaseScraper` and defines a `site_name` class attribute and a `search()` method.  See `themuse_scraper.py` for guidance.
3. Register the new scraper in `job_scraper/scrapers/__init__.py` by importing the class and adding it to the `SCRAPERS` dictionary.
4. Respect the site’s terms of service and be mindful of rate limiting.

## Limitations & future work

This project is an MVP and intentionally conservative in scope:

- **Only one site implemented** – The Muse API is used because it’s freely accessible.  LinkedIn and Indeed both require more sophisticated scraping or authorised APIs, and therefore are left as future work.  Implementing these would require handling pagination, JavaScript rendering, bot detection and possibly login.
- **Basic filtering** – Location and recency filtering are applied, but additional filters (job level, category, company) are not exposed in the CLI yet.
- **No scheduling** – The scraper is run manually.  It could be scheduled via cron or integrated into a larger application.

Contributions and pull requests are welcome!