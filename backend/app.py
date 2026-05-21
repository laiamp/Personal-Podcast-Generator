from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

from routes import podcasts as podcasts_router
from routes import sources as sources_router
import db

app = FastAPI(title="Personal Podcast Generator - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # ensure DB client is created
    db.get_db()


@app.get("/health")
async def health():
    mongodb_status = "ok"

    try:
        await db.get_client().admin.command("ping")
    except Exception:
        mongodb_status = "down"

    return {"status": "ok", "mongodb": mongodb_status}


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(sources_router.router)
app.include_router(podcasts_router.router)
