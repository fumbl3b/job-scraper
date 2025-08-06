"""
Base class for job board scrapers.

Each scraper must inherit from this class and implement the ``search()`` method.
The ``site_name`` class attribute is used to register the scraper.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional


@dataclass
class JobPosting:
    """Represents a single job posting returned by a scraper."""

    title: str
    company: str
    location: str
    publication_date: datetime
    description: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        """Convert the job posting to a dictionary of simple types for easy
        serialisation (e.g. JSON or CSV).
        """
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "publication_date": self.publication_date.isoformat(),
            "description": self.description,
            "url": self.url,
        }


class BaseScraper(abc.ABC):
    """
    Abstract base class for all job board scrapers.

    Subclasses should define the ``site_name`` attribute and implement the
    ``search`` method.  The ``search`` method should return an iterable of
    :class:`JobPosting` objects.
    """

    #: Unique identifier for the job board (e.g. ``"themuse"``)
    site_name: str = ""

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<{self.__class__.__name__} site={self.site_name!r}>"

    @abc.abstractmethod
    def search(
        self,
        query: str,
        *,
        location: Optional[str] = None,
        days: Optional[int] = None,
        max_results: Optional[int] = None,
    ) -> Iterable[JobPosting]:
        """Search for jobs.

        Args:
            query: Keywords to search for (e.g. "software engineer").
            location: Optional location filter (e.g. "Philadelphia, PA").
            days: Optional maximum age of the posting in days.  If supplied,
                only jobs with a publication date within the past ``days``
                (relative to now) should be returned.
            max_results: Optional maximum number of results to return.  If
                ``None``, return as many as the site provides.

        Returns:
            An iterable of job postings.
        """

    def _within_days(self, date: datetime, days: Optional[int]) -> bool:
        """Return True if ``date`` is within ``days`` of now, or if ``days``
        is None.
        """
        if days is None:
            return True
        delta = datetime.utcnow() - date
        return delta.days < days