from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
import db

router = APIRouter()


@router.get("/sources")
async def list_sources(limit: int = 50):
    database = db.get_db()
    try:
        docs = await database["sources"].find().sort("scraped_at", -1).to_list(limit)
        return jsonable_encoder(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
