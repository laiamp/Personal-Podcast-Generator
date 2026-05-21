import asyncio
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import db
from scrapers.hackernews import scrape_hackernews


async def fetch_hackernews_items(query: str = "AI") -> list[dict[str, object]]:
    return await asyncio.to_thread(scrape_hackernews, query)


async def main():
    print("Running Hacker News scraper...")
    items = await fetch_hackernews_items("AI")
    if not items:
        print("No items scraped.")
        return

    database = db.get_db()
    # Insert items, avoid duplicates by source_url when possible
    for item in items:
        existing = await database["sources"].find_one({"source_url": item["source_url"]})
        if existing:
            print(f"Skipping existing: {item['source_url']}")
            continue
        res = await database["sources"].insert_one(item)
        print(f"Inserted source id={res.inserted_id}")


if __name__ == "__main__":
    asyncio.run(main())
