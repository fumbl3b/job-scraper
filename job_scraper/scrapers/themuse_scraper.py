"""
Scraper for The Muse job board.

The Muse exposes a public API that we can query without authentication:
```
https://www.themuse.com/api/public/jobs
```

The API supports parameters such as:
* ``q`` – keywords (free‑text search)
* ``location`` – location string (city, state, or remote)
* ``page`` – page number (1‑indexed)

This scraper fetches jobs page by page, applies client‑side filtering on
publication date and location, and yields :class:`JobPosting` instances.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, Optional

import dateutil.parser
import requests

from .base import BaseScraper, JobPosting


logger = logging.getLogger(__name__)


class TheMuseScraper(BaseScraper):
    """Scraper implementation for The Muse job board."""

    site_name = "themuse"

    API_ENDPOINT = "https://www.themuse.com/api/public/jobs"

    def search(
        self,
        query: str,
        *,
        location: Optional[str] = None,
        days: Optional[int] = None,
        max_results: Optional[int] = None,
    ) -> Iterable[JobPosting]:
        """Search The Muse API for jobs matching the criteria.

        See :meth:`BaseScraper.search` for argument details.
        """
        results: list[JobPosting] = []
        page = 1
        fetched = 0
        total_pages: Optional[int] = None
        while True:
            # If the API reports the total page count, stop when we've
            # exceeded it.  The API is 1‑indexed.
            if total_pages is not None and page > total_pages:
                break
            params = {"page": page}
            # Add query and location parameters if supplied
            if query:
                params["q"] = query
            if location:
                params["location"] = location
            # Request the API
            try:
                response = requests.get(self.API_ENDPOINT, params=params, timeout=10)
            except Exception as exc:
                logger.error("Error contacting The Muse API: %s", exc)
                break
            if response.status_code != 200:
                logger.error(
                    "The Muse API returned non‑200 status %s for page %s", response.status_code, page
                )
                break
            data = response.json()
            jobs = data.get("results", [])
            if not jobs:
                break  # no more results
            for job in jobs:
                # Parse publication date
                try:
                    pub_date = dateutil.parser.isoparse(job["publication_date"]).replace(tzinfo=None)
                except Exception:
                    continue
                if not self._within_days(pub_date, days):
                    continue
                # Filter by location if provided: at least one of the job's locations must
                # include the search location (case‑insensitive substring match).
                if location:
                    loc_names = [loc.get("name", "") for loc in job.get("locations", [])]
                    match = any(location.lower() in loc_name.lower() for loc_name in loc_names)
                    # Also include remote/flexible jobs when searching by location
                    remote_keywords = ["remote", "flexible"]
                    if not match:
                        match = any(
                            any(keyword in loc_name.lower() for keyword in remote_keywords)
                            for loc_name in loc_names
                        )
                    if not match:
                        continue
                # Build the JobPosting object
                title = job.get("name", "").strip()
                company_name = job.get("company", {}).get("name", "").strip()
                # Use the first location name if available; else empty string
                loc = job.get("locations", [])
                if loc:
                    loc_str = loc[0].get("name", "")
                else:
                    loc_str = ""
                description = self._strip_html(job.get("contents", ""))
                # Use the job's public URL (refs.page) if available
                url = job.get("refs", {}).get("landing_page", "")
                posting = JobPosting(
                    title=title,
                    company=company_name,
                    location=loc_str,
                    publication_date=pub_date,
                    description=description,
                    url=url,
                )
                results.append(posting)
                fetched += 1
                if max_results is not None and fetched >= max_results:
                    return results
            # Advance to next page
            # Update the total number of pages after the first request
            if total_pages is None:
                try:
                    total_pages = int(data.get("page_count", 0))
                except Exception:
                    total_pages = 0
            # Move to next page
            page += 1
        return results

    @staticmethod
    def _strip_html(html: str) -> str:
        """Very naive HTML tags stripper for job descriptions.

        The Muse returns HTML in the `contents` field.  This helper removes
        tags for a cleaner plain‑text output.  For a production scraper
        you might use BeautifulSoup instead.
        """
        import re

        # Remove script/style tags and their contents
        html = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        # Remove all HTML tags
        text = re.sub(r"<[^>]+>", "", html)
        # Condense whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()