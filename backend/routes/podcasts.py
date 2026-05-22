from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from services.podcast_generation import test_generate_podcast, generate_podcast
from db import get_db


router = APIRouter(prefix="/podcasts", tags=["podcasts"])


class PodcastGenerateRequest(BaseModel):
    user_id: str = Field(..., description="User ID as a MongoDB ObjectId string")
    interests_query: str | None = Field(default=None, description="Optional search text to filter sources")
    voice_type: str = Field(default="multi_host_banter")
    source_limit: int = Field(default=5, ge=1, le=25)


@router.post("/generate")
async def create_podcast(payload: PodcastGenerateRequest) -> dict[str, Any]:
    try:
        result = await generate_podcast(
            user_id=payload.user_id,
            interests_query=payload.interests_query,
            voice_type=payload.voice_type,
            source_limit=payload.source_limit,
        )
        return jsonable_encoder(result)
    except ValueError as exc:
        print(f"Validation error during podcast generation: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Unexpected error during podcast generation: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("")
async def list_podcasts(limit: int = 20) -> list[dict[str, Any]]:
    database = get_db()
    try:
        docs = await database["podcasts"].find().sort("created_at", -1).to_list(limit)
        return jsonable_encoder(docs)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
