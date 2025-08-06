"""
Stub scraper for LinkedIn.

LinkedIn strictly forbids scraping of its job postings and requires authentication,
handling of dynamic JavaScript content and anti‑bot measures.  This class is
provided solely as a placeholder for future work.
"""

from __future__ import annotations

from typing import Iterable, Optional

from .base import BaseScraper, JobPosting


class LinkedInScraper(BaseScraper):
    """Placeholder scraper for LinkedIn."""

    site_name = "linkedin"

    def search(
        self,
        query: str,
        *,
        location: Optional[str] = None,
        days: Optional[int] = None,
        max_results: Optional[int] = None,
    ) -> Iterable[JobPosting]:
        raise NotImplementedError(
            "LinkedIn scraping is not implemented. LinkedIn terms of service prohibit automated scraping; please use their official API or other tools."
        )