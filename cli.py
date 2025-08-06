#!/usr/bin/env python3
"""
Command‑line interface for the job scraper.

Example usage:

```
python cli.py --site themuse --query "data scientist" --location "New York, NY" --days 3 --max-results 30 --output jobs.json
```
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List

from tabulate import tabulate

from job_scraper import get_scraper, SCRAPERS


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape recent job postings from supported sites.")
    parser.add_argument(
        "--site",
        default="themuse",
        choices=list(SCRAPERS.keys()),
        help="Which job site to query (default: %(default)s)",
    )
    parser.add_argument(
        "--query",
        "-q",
        required=True,
        help="Keywords to search for, e.g. 'software engineer'",
    )
    parser.add_argument(
        "--location",
        "-l",
        default=None,
        help="Optional location filter, e.g. 'Philadelphia, PA'",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="Maximum age of job postings in days (default: %(default)s). Use 0 to disable filtering.",
    )
    parser.add_argument(
        "--max-results",
        "-m",
        type=int,
        default=50,
        help="Maximum number of results to return (default: %(default)s).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Optional output file.  Supports .json and .csv extensions.  If omitted, results are printed to the console.",
    )
    return parser.parse_args(argv)


def format_console(jobs) -> None:
    """Print a list of jobs as a table to stdout."""
    rows = []
    for job in jobs:
        rows.append([
            job.title,
            job.company,
            job.location,
            job.publication_date.strftime("%Y-%m-%d"),
            job.url,
        ])
    headers = ["Title", "Company", "Location", "Posted", "URL"]
    table = tabulate(rows, headers=headers, tablefmt="github")
    print(table)


def write_output(jobs, path: str) -> None:
    """Write the list of job postings to the given output file.

    The format is inferred from the file extension.  JSON (``.json``) and CSV
    (``.csv``) are supported.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump([job.to_dict() for job in jobs], f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(jobs)} jobs to {path}")
    elif ext == ".csv":
        import csv

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "company", "location", "publication_date", "description", "url"],
            )
            writer.writeheader()
            for job in jobs:
                writer.writerow(job.to_dict())
        print(f"Wrote {len(jobs)} jobs to {path}")
    else:
        raise ValueError(f"Unsupported output format '{ext}'. Please use .json or .csv.")


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    site = args.site.lower()
    scraper = get_scraper(site)
    # If days is 0, treat as no filtering
    days = args.days if args.days > 0 else None
    try:
        jobs = list(
            scraper.search(
                args.query,
                location=args.location,
                days=days,
                max_results=args.max_results,
            )
        )
    except NotImplementedError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    # Sort jobs by publication date descending
    jobs.sort(key=lambda j: j.publication_date, reverse=True)
    if args.output:
        write_output(jobs, args.output)
    else:
        format_console(jobs)


if __name__ == "__main__":
    main()