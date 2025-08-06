"""
Scraper registry

This module exposes all available job board scrapers and registers them in a
dictionary keyed by their `site_name`.  New scrapers should be imported and
added to the `SCRAPERS` dictionary here.
"""

from .base import BaseScraper
from .themuse_scraper import TheMuseScraper
from .indeed_scraper import IndeedScraper
from .linkedin_scraper import LinkedInScraper
from .remotive_scraper import RemotiveScraper


# Registry mapping site name to scraper class
SCRAPERS = {
    TheMuseScraper.site_name: TheMuseScraper,
    IndeedScraper.site_name: IndeedScraper,
    LinkedInScraper.site_name: LinkedInScraper,
    RemotiveScraper.site_name: RemotiveScraper,
}


__all__ = ["BaseScraper", "TheMuseScraper", "IndeedScraper", "LinkedInScraper", "SCRAPERS"]