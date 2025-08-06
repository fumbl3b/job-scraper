"""
Stub scraper for Indeed.

Indeed’s website aggressively blocks scraping and requires a complex workflow or
API access to retrieve job listings.  This class is provided as a placeholder
for future development.
"""

from __future__ import annotations

from typing import Iterable, Optional

from .base import BaseScraper, JobPosting


class IndeedScraper(BaseScraper):
    """Placeholder scraper for Indeed."""

    site_name = "indeed"

    def search(
        self,
        query: str,
        *,
        location: Optional[str] = None,
        days: Optional[int] = None,
        max_results: Optional[int] = None,
    ) -> Iterable[JobPosting]:
        raise NotImplementedError(
            "Indeed scraping is not implemented. Indeed restricts scraping; consider using their official API or third‑party services."
        )