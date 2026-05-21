from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests


HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"


def _fetch_jina_content(url: str) -> str:
    """Scrapes the external URL using Jina Reader API to get clean content."""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        # Requesting JSON from Jina gives a clean, structured payload
        response = requests.get(jina_url, headers={"Accept": "application/json"}, timeout=15)
        if response.status_code == 200:
            return response.json().get("data", {}).get("content", "")
    except Exception:
        # Silently fail and fallback if the website blocks scraping or Jina times out
        pass
    return ""


def _build_source_document(hit: dict[str, Any]) -> dict[str, Any]:
    created_at = hit.get("created_at_i")
    event_date = (
        datetime.fromtimestamp(created_at, tz=timezone.utc)
        if isinstance(created_at, int)
        else datetime.now(tz=timezone.utc)
    )

    external_url = hit.get("url")
    hn_url = f"https://news.ycombinator.com/item?id={hit['objectID']}"
    
    # Try to grab the deep content of the article via Jina Reader.
    # Fallback to standard HN text (story_text or comment_text) if it's an internal-only post.
    content = ""
    if external_url:
        content = _fetch_jina_content(external_url)
        
    if not content:
        content = hit.get("story_text") or hit.get("comment_text") or ""

    return {
        "title": hit.get("title") or "Hacker News story",
        "location": "Hacker News",
        "event_date": event_date,
        "scraped_at": datetime.now(tz=timezone.utc),
        "summary": content,  # Now contains the actual cleaned-up article content!
        "category": "news",
        "source_url": external_url or hn_url,
        "source_type": "hackernews",
        "hn_object_id": hit.get("objectID"),
        "author": hit.get("author"),
        "points": hit.get("points", 0),
        "num_comments": hit.get("num_comments", 0),
    }


def scrape_hackernews(query: str = "") -> list[dict[str, Any]]:
    params = {"query": query, "tags": "story", "hitsPerPage": 12}
    response = requests.get(HN_SEARCH_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    hits = payload.get("hits", [])

    return [_build_source_document(hit) for hit in hits if hit.get("objectID")]


if __name__ == "__main__":
    # Test with your specific target query!
    for item in scrape_hackernews("Karpathy Anthropic"):
        print(f"TITLE: {item['title']}")
        print(f"URL: {item['source_url']}")
        print(f"CONTENT PREVIEW:\n{item['summary'][:500]}...\n")
        print("-" * 50)