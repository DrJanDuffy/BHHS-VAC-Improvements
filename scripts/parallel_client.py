"""Thin wrapper around the Parallel Search API (https://api.parallel.ai/v1/search).

Requires PARALLEL_API_KEY in the environment. Every call is metered by the
caller against config/loop_config.json's max_parallel_search_calls_per_run —
this module does not enforce a budget itself, it just makes the call and
reports what it cost.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

import requests

SEARCH_URL = "https://api.parallel.ai/v1/search"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 2


class ParallelAPIError(RuntimeError):
    pass


@dataclass
class SearchResult:
    url: str
    title: str
    excerpts: list[str] = field(default_factory=list)
    publish_date: str | None = None


@dataclass
class SearchResponse:
    search_id: str
    results: list[SearchResult]
    calls_used: int = 1


def search(objective: str, search_queries: list[str], max_results: int = 5) -> SearchResponse:
    """Run one Parallel Search API call. Raises ParallelAPIError on failure
    after retries — callers should treat that as a skipped check, not a dead
    link or a superseded tip; an API outage must never be read as a finding.
    """
    api_key = os.environ.get("PARALLEL_API_KEY")
    if not api_key:
        raise ParallelAPIError("PARALLEL_API_KEY is not set")

    payload = {
        "objective": objective,
        "search_queries": search_queries,
        "max_results": max_results,
    }
    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(SEARCH_URL, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                results = [
                    SearchResult(
                        url=r.get("url", ""),
                        title=r.get("title", ""),
                        excerpts=r.get("excerpts", []) or [],
                        publish_date=r.get("publish_date"),
                    )
                    for r in data.get("results", [])
                ]
                return SearchResponse(search_id=data.get("search_id", ""), results=results, calls_used=1)
            last_err = ParallelAPIError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        except requests.RequestException as exc:  # noqa: PERF203
            last_err = exc
        if attempt < MAX_RETRIES:
            time.sleep(1.5 * (attempt + 1))

    raise ParallelAPIError(str(last_err))
