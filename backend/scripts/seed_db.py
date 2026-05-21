from __future__ import annotations

import argparse
import asyncio
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from pathlib import Path

from bson import ObjectId

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import db
from scripts.run_scraper import fetch_hackernews_items
from services.podcast_generation import build_source_snapshot


SEED = 42
BASE_TIME = datetime(2026, 5, 21, 8, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class UserSeed:
    _id: ObjectId
    email: str
    demographics: dict[str, Any]
    preferences: dict[str, Any]
    created_at: datetime


def _oid(hex_suffix: str) -> ObjectId:
    return ObjectId(f"65f1c2a1b3c4d5e6f7a8{hex_suffix}")


def build_users() -> list[dict[str, Any]]:
    return [
        {
            "_id": _oid("b9c0"),
            "email": "barcelona.founder@domain.com",
            "demographics": {"gender": "female", "age": 31},
            "preferences": {
                "periodicity": "daily",
                "voice_type": "multi_host_banter",
                "interests": ["AI", "startups", "funding-milestones"],
            },
            "created_at": BASE_TIME - timedelta(days=4),
        },
        {
            "_id": _oid("b9c1"),
            "email": "sarah.pm@domain.com",
            "demographics": {"gender": "female", "age": 28},
            "preferences": {
                "voice_type": "analytical",
                "interests": ["product", "ai-ops", "open-source"],
            },
            "created_at": BASE_TIME - timedelta(days=9),
        },
        {
            "_id": _oid("b9c2"),
            "email": "marc.engineer@domain.com",
            "demographics": {"gender": "male", "age": 36},
            "preferences": {
                "voice_type": "solo",
                "interests": ["hardware", "llms", "devtools"],
            },
            "created_at": BASE_TIME - timedelta(days=15),
        },
        {
            "_id": _oid("b9c3"),
            "email": "ana.research@domain.com",
            "demographics": {"gender": "female", "age": 42},
            "preferences": {
                "periodicity": "on-demand",
                "voice_type": "solo",
                "interests": ["research", "funding", "model-release"],
            },
            "created_at": BASE_TIME - timedelta(days=21),
        },

    ]


async def build_sources() -> list[dict[str, Any]]:
    return await fetch_hackernews_items("AI")


def build_podcasts(users: list[dict[str, Any]], sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    podcasts: list[dict[str, Any]] = []
    podcast_sources = [
        sources[0:3],
        sources[3:5],
        sources[5:8],
        sources[1:4],
        sources[6:10],
    ]
    user_cycle = [user["_id"] for user in users]

    for index, selected_sources in enumerate(podcast_sources):
        created_at = BASE_TIME - timedelta(days=index, hours=index * 2)
        total_seconds = 180 + index * 30
        segment_length = max(30, total_seconds // max(1, len(selected_sources)))
        podcast = {
            "_id": ObjectId(),
            "user_id": user_cycle[index % len(user_cycle)],
            "audio_url": f"/static/audio/podcast_seed_{index + 1}.mp3",
            "duration_seconds": total_seconds,
            "created_at": created_at,
            "source_snapshots": [build_source_snapshot(source) for source in selected_sources],
            "script": "\n".join(
                [
                    f"Intro: A concise briefing about {selected_sources[0]['title']}",
                    f"Middle: connect it with {selected_sources[-1]['title']} and the weekly trend.",
                    "Outro: keep the pace tight and actionable.",
                ]
            ),
            "source_count": len(selected_sources),
            "generation_context": {
                "user_id": str(user_cycle[index % len(user_cycle)]),
                "interests_query": "AI startups and product launches",
                "generated_at": created_at.isoformat(),
            },
        }
        podcasts.append(podcast)
    return podcasts


def build_events(users: list[dict[str, Any]], podcasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    event_types = ["podcast_open", "podcast_play", "podcast_dropoff", "podcast_complete"]

    for index, podcast in enumerate(podcasts):
        user = users[index % len(users)]
        duration = podcast["duration_seconds"]
        listened = max(20, duration - 15 * (index + 1))
        events.append(
            {
                "_id": ObjectId(),
                "user_id": user["_id"],
                "podcast_id": podcast["_id"],
                "event_type": random.choice(event_types),
                "metadata": {
                    "stopped_at_second": listened,
                    "total_duration_seconds": duration,
                    "percentage_completed": round((listened / duration) * 100, 1),
                },
                "timestamp": podcast["created_at"] + timedelta(minutes=35),
            }
        )

    return events


async def seed_database(reset: bool = False) -> None:
    random.seed(SEED)
    database = db.get_db()

    users = build_users()
    sources = await build_sources()
    podcasts = build_podcasts(users, sources)
    events = build_events(users, podcasts)

    if reset:
        await database["events"].delete_many({})
        await database["podcasts"].delete_many({})
        await database["sources"].delete_many({})
        await database["users"].delete_many({})

    await database["users"].insert_many(users)
    await database["sources"].insert_many(sources)
    await database["podcasts"].insert_many(podcasts)
    await database["events"].insert_many(events)

    print(f"Seeded {len(users)} users, {len(sources)} sources, {len(podcasts)} podcasts, {len(events)} events.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the MongoDB database with deterministic fake data.")
    parser.add_argument("--reset", action="store_true", help="Clear collections before inserting seed data.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(seed_database(reset=args.reset))


if __name__ == "__main__":
    main()
