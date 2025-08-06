"""
Scraper for Remotive.io remote job board.

Remotive provides a public API for remote jobs:

    https://remotive.com/api/remote-jobs?search=python

The API returns a JSON object with a list of jobs under the ``jobs`` key.  Each
job includes fields such as ``title``, ``company_name``, ``publication_date``
and ``candidate_required_location``.  This scraper supports keyword search,
location filtering (by substring on the required location), and recency
filtering based on publication date.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, Optional

import dateutil.parser
import requests

from .base import BaseScraper, JobPosting


logger = logging.getLogger(__name__)


class RemotiveScraper(BaseScraper):
    """Scraper implementation for Remotive.io."""

    site_name = "remotive"
    API_ENDPOINT = "https://remotive.com/api/remote-jobs"

    def search(
        self,
        query: str,
        *,
        location: Optional[str] = None,
        days: Optional[int] = None,
        max_results: Optional[int] = None,
    ) -> Iterable[JobPosting]:
        params = {}
        if query:
            params["search"] = query
        try:
            response = requests.get(self.API_ENDPOINT, params=params, timeout=10)
        except Exception as exc:
            logger.error("Error contacting Remotive API: %s", exc)
            return []
        if response.status_code != 200:
            logger.error("Remotive API returned status %s", response.status_code)
            return []
        data = response.json()
        jobs = data.get("jobs", [])
        results: list[JobPosting] = []
        for job in jobs:
            # Publication date as ISO string
            try:
                pub_date = dateutil.parser.isoparse(job.get("publication_date")).replace(tzinfo=None)
            except Exception:
                continue
            if not self._within_days(pub_date, days):
                continue
            # Filter by location: candidate_required_location is a string like "Worldwide" or "USA Only"
            job_location = job.get("candidate_required_location", "").strip()
            if location:
                # Accept if location substring matches (case‑insensitive)
                if location.lower() not in job_location.lower():
                    continue
            title = job.get("title", "").strip()
            company_name = job.get("company_name", "").strip()
            url = job.get("url", "").strip()
            description = self._strip_html(job.get("description", ""))
            posting = JobPosting(
                title=title,
                company=company_name,
                location=job_location,
                publication_date=pub_date,
                description=description,
                url=url,
            )
            results.append(posting)
            if max_results is not None and len(results) >= max_results:
                break
        return results

    @staticmethod
    def _strip_html(html: str) -> str:
        """Naively remove HTML tags from Remotive job descriptions."""
        import re

        html = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()