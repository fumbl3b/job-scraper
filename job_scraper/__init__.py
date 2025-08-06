"""
Job Scraper package

This package exposes a registry of supported job board scrapers and a base class for
implementing new scrapers.  Use the `get_scraper` function to instantiate a
scraper by name.
"""

from .scrapers import SCRAPERS


def get_scraper(site_name: str):
    """Return an instance of the scraper for the given site name.

    Args:
        site_name: The identifier of the site (e.g. ``"themuse"``).

    Raises:
        KeyError: If the scraper is not registered.
    """
    site = site_name.lower()
    if site not in SCRAPERS:
        raise KeyError(f"Unknown site '{site_name}'. Available sites: {', '.join(SCRAPERS.keys())}")
    return SCRAPERS[site]()


__all__ = ["get_scraper", "SCRAPERS"]