"""Fetch ALL pages from a paginated API with retries, timeouts and 429 handling."""
import time

import requests

TIMEOUT = 30


def fetch_all(url, headers=None, params=None, page_size=100, max_pages=1000):
    """Offset/limit pagination. Stops on an empty or short page."""
    session = requests.Session()
    results, offset = [], 0
    for _ in range(max_pages):  # safety cap against infinite loops
        query = dict(params or {}, limit=page_size, offset=offset)
        resp = _get_with_retry(session, url, headers, query)
        page = resp.json()
        items = page.get("data", page) if isinstance(page, dict) else page
        if not items:
            break
        results.extend(items)
        if len(items) < page_size:
            break
        offset += page_size
    return results


def fetch_all_cursor(url, headers=None, params=None):
    """Cursor/Link pagination: follow `next` until it is missing."""
    session, results, next_url = requests.Session(), [], url
    query = dict(params or {})
    while next_url:
        resp = _get_with_retry(session, next_url, headers, query)
        body = resp.json()
        results.extend(body.get("data", []))
        next_url, query = body.get("next"), {}  # `next` already contains the query
    return results


def _get_with_retry(session, url, headers, params, tries=4):
    wait = 1
    for attempt in range(tries):
        try:
            resp = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == tries - 1:
                raise
        else:
            if resp.status_code == 429:  # rate limited: honour Retry-After
                wait = int(resp.headers.get("Retry-After", wait))
            elif resp.status_code >= 500:  # transient server error: back off
                pass
            else:
                resp.raise_for_status()  # 4xx: our fault, do NOT retry
                return resp
            if attempt == tries - 1:
                resp.raise_for_status()
        time.sleep(wait)
        wait *= 2
