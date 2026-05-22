from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from bson import ObjectId

from db import get_db
from llm.openai_client import OpenAIClient
from .validation import validate_script
from .source_cleaning import clean_source_summary


TEST_AUDIO_URL = "/audio/test3.mp3"


def build_source_snapshot(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "_id": str(source["_id"]) if source.get("_id") else None,
        "title": source.get("title"),
        "summary": clean_source_summary(source.get("summary")),
        "source_url": source.get("source_url"),
        "source_type": source.get("source_type"),
        "category": source.get("category"),
        "scraped_at": source.get("scraped_at").isoformat() if isinstance(source.get("scraped_at"), datetime) else source.get("scraped_at"),
    }


def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, list):
            serialized[key] = [
                _serialize_document(item) if isinstance(item, dict) else (str(item) if isinstance(item, ObjectId) else item)
                for item in value
            ]
        elif isinstance(value, dict):
            serialized[key] = _serialize_document(value)
        else:
            serialized[key] = value
    return serialized




async def _load_sources(limit: int = 5, query: str | None = None) -> list[dict[str, Any]]:
    database = get_db()
    mongo_query: dict[str, Any] = {}
    if query:
        mongo_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"summary": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"source_type": {"$regex": query, "$options": "i"}},
            ]
        }

    cursor = database["sources"].find(mongo_query).sort("scraped_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def generate_podcast(
    *,
    user_id: str,
    interests_query: str | None = None,
    voice_type: str = "multi_host_banter",
    source_limit: int = 5,
) -> dict[str, Any]:
    database = get_db()
    sources = await _load_sources(limit=source_limit, query=interests_query)
  

    user_context = {
        "user_id": user_id,
        "interests_query": interests_query,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    openai_client = OpenAIClient()
    script = openai_client.generate_podcast_script(
        sources,
        voice_type=voice_type,
        user_context=user_context,
    )
    # Validate the generated script for basic quality before synthesis
    try:
        validate_script(script)
    except Exception as exc:  # re-raise with clearer context
        raise ValueError(f"Generated script failed validation: {exc}") from exc

    audio_dir = Path("static") / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_filename = f"podcast_{uuid4().hex}.mp3"
    audio_path = audio_dir / audio_filename

    # Synthesize audio for real generation flows.
    from tts.elevenlabs_client import ElevenLabsClient

    elevenlabs_client = ElevenLabsClient()
    elevenlabs_client.synthesize_to_file(script, audio_path)

    source_ids = [source.get("_id") for source in sources if source.get("_id")]
    total_duration_seconds = int(max(60, min(600, len(script.split()) * 0.5)))
    segment_count = max(1, len(sources))
    segment_length = max(1, total_duration_seconds // segment_count)

    podcast_document = {
        "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
        # Publicly served static audio lives at the site root (e.g. /audio/...)
        "audio_url": f"/audio/{audio_filename}",
        "duration_seconds": total_duration_seconds,
        "created_at": datetime.now(tz=timezone.utc),
        "source_snapshots": [build_source_snapshot(source) for source in sources],
        "timeline_segments": [
            {
                "source_id": source_id,
                "start_second": index * segment_length,
                "end_second": total_duration_seconds if index == segment_count - 1 else min(total_duration_seconds, (index + 1) * segment_length),
                "topic": source.get("title", "Untitled story"),
            }
            for index, (source_id, source) in enumerate(zip(source_ids, sources, strict=False))
        ],
        "script": script,
        "source_count": len(sources),
        "generation_context": user_context,
    }

    result = await database["podcasts"].insert_one(podcast_document)
    podcast_document["_id"] = result.inserted_id
    return {
        "podcast": _serialize_document(podcast_document),
        "sources": [_serialize_document(source) for source in sources],
    }



async def test_generate_podcast(
    *,
    user_id: str,
    interests_query: str | None = "Andrej Karpathy",
    voice_type: str = "multi_host_banter",
    source_limit: int = 5,
) -> dict[str, Any]:
    database = get_db()
    sources = await _load_sources(limit=source_limit, query=interests_query)

    user_context = {
        "user_id": user_id,
        "interests_query": interests_query,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    script = "This is a test podcast script."

    # Validate the generated script for basic quality before synthesis
    try:
        validate_script(script)
    except Exception as exc:  # re-raise with clearer context
        raise ValueError(f"Generated script failed validation: {exc}") from exc

    audio_filename = "test3.mp3"
    audio_path = Path("static") / "audio" / audio_filename
    if not audio_path.exists():
        raise FileNotFoundError(f"Expected test audio file at {audio_path}")
  


    source_ids = [source.get("_id") for source in sources if source.get("_id")]
    total_duration_seconds = int(max(60, min(600, len(script.split()) * 0.5)))
    segment_count = max(1, len(sources))
    segment_length = max(1, total_duration_seconds // segment_count)

    podcast_document = {
        "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
        "audio_url": f"/static/audio/{audio_filename}",
        "duration_seconds": total_duration_seconds,
        "created_at": datetime.now(tz=timezone.utc),
        "source_snapshots": [build_source_snapshot(source) for source in sources],
        "timeline_segments": [
            {
                "source_id": source_id,
                "start_second": index * segment_length,
                "end_second": total_duration_seconds if index == segment_count - 1 else min(total_duration_seconds, (index + 1) * segment_length),
                "topic": source.get("title", "Untitled story"),
            }
            for index, (source_id, source) in enumerate(zip(source_ids, sources, strict=False))
        ],
        "script": script,
        "source_count": len(sources),
        "generation_context": user_context,
    }

    result = await database["podcasts"].insert_one(podcast_document)
    podcast_document["_id"] = result.inserted_id
    return {
        "podcast": _serialize_document(podcast_document),
        "sources": [_serialize_document(source) for source in sources],
    }
