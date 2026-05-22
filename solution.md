# Personal Podcast Generator: Architecture & Solution Design

https://github.com/laiamp/Personal-Podcast-Generator.git
---

## 1. System Architecture

The platform follows a decoupled, three-tier design that connects data ingestion, LLM processing, and cloud-based audio generation.

### Core Components

**Data Aggregation & Ingestion Layer**  
Scrapes and cleans text from external sources. Raw metadata (titles, links, body text, engagement signals like points or comment counts) gets stored locally before any generation kicks in.

**The Backend Broker (Node.js / FastAPI)**  
The middle layer handling database access, user context mapping, prompt construction, data validation, and proxying requests to third-party APIs.

**Persistence Layer (MongoDB)**  
Uses a document model to store snapshots of raw inputs alongside finished podcast records, including final scripts, timelines, metadata, and links to audio in cloud storage.

**AI Integration (OpenAI + ElevenLabs Clients)**  
Talks to the foundation models. Handles text processing, thematic abstraction, and assembling the audio layers.

---

## 2. Data Flow & LLM Pipeline

Raw web documents become a coherent audio narrative through this path:

```
[ Scrapers / Feeds ] ----> ( Clean & Filter ) ----> [ MongoDB Stash ]
                                                          │
   ┌──────────────────────────────────────────────────────┘
   ▼
[ Backend Orchestrator ]
   │
   ├──-> 1. Load source metadata + user profile context
   ├──-> 2. Build structured prompts (system + user vectors)
   ├──-> 3. Send context window ----> [ OpenAI Client API ]
   │                                          │
   ▼                                          ▼
[ ElevenLabs TTS API ] <---- ( Validation Filter ) <---- [ Raw Script Output ]
   │
   ▼
[ Final Asset Storage (.mp3) ] ----> Update Record in MongoDB
```

### Pipeline Steps

1. **Ingestion & State Validation**  
   The system queries MongoDB for the most relevant, unread source items based on the user's profile (`user_context`). Right now this runs as an on-demand script, but it needs to become a scheduled cron job.

2. **Prompt Assembly**  
   The system pulls fields like `title`, `summary`, `url`, and numeric ranking signals (`points`, `num_comments`). It combines these with structural rules (target duration, voice type) using `build_podcast_prompt()`.

3. **Script Generation (LLM)**  
   The assembled system and user text blocks go straight to OpenAI's completion models. The LLM processes the context and returns a continuous monologue-style spoken script.

4. **Content Validation**  
   The raw script runs through a verification module (`validation.py`) to check timing parameters and safety constraints.

5. **Audio Synthesis**  
   The validated script is sent to ElevenLabs' Text-to-Speech models, which return high-fidelity binary audio buffers.

---

## 3. MongoDB Collections
Since a podcast can have multiple sources and sources may vary of shape, I opted for a document-based database.

**Users Collection**  
Stores profiles, account details, and personalization settings used when generating scripts.  
Key fields: User ID, email, password hash, registration date, generation preferences (target podcast length, favorite topics, chosen AI voice ID).

**Sources Collection**  
Tracks raw articles, stories, and RSS feed items pulled from external sources before audio generation.  
Key fields: Source ID, article title, URL, raw text content, engagement stats (upvotes, comment counts), ingestion timestamp, and a status flag indicating whether it has been used yet.

**Podcasts Collection**  
Represents a finished audio episode with an embedded snapshot of the original sources.  
Key fields: Podcast ID, User ID reference, cloud storage link to the final `.mp3`, audio duration, creation date, and the generated script text.  
Embedded array: A list of the exact Sources used, keeping the record complete even if the original articles are later deleted.

**Events Collection**  
An append-only log for system milestones and user interactions with the audio player. Used for debugging and analytics.  
Key fields: Event ID, User ID reference, timestamp, event type.  
Tracked actions: System events (`GENERATION_STARTED`, `AUDIO_GENERATION_SUCCESS`) and player activity (`PLAYER_PAUSED`, `PLAYER_RESUMED`).

---

## 4. Implementation Status

| Component | Status | Notes |
| :--- | :--- | :--- |
| **Ingestion Engine** | Implemented | Scrapes sources, cleans markup, persists clean snapshots to MongoDB. |
| **Source Relevance & Ranking** | Not implemented | The logic for surfacing the most relevant sources per user is still being defined. The likely direction is a hybrid approach combining keyword-based scoring (TF-IDF) with embedding-based semantic matching (similar to CLIP-style models). |
| **Prompt Orchestration** | Implemented | `build_podcast_prompt()` dynamically compiles text parameters into rich input payloads. |
| **Sequential AI Execution** | Implemented | Runs synchronous OpenAI completion calls, followed by ElevenLabs TTS calls in sequence. |
| **Script Validation** | Template only | Placeholder file exists at `validation.py`. Still needs real rules for word count checks and linguistic consistency before audio rendering. |
| **Chunked Streaming (WebSockets)** | Not implemented | Planned optimization. Currently the full script processes end to end, which creates latency. |


## 5. Future Optimization: Streaming via Concurrent WebSockets

To cut down the startup delay from generating a full audio script sequentially, the system will move to chunked execution:

```
[ OpenAI Streaming Gen ] ----(token chunks)----> [ Concurrent Validation Worker ]
                                                          │
                                                   (approved paragraphs)
                                                          ▼
[ Client Browser ] <----(raw audio packets)---- [ ElevenLabs Audio Stream ]
```

An open WebSocket connection will stream text blocks from OpenAI to a validation worker in parallel. Approved segments move immediately to ElevenLabs for TTS. The resulting audio chunks push straight to the client as a continuous binary stream, bringing the time-to-first-audio down to seconds.