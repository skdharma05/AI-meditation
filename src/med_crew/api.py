import os
import uuid
import json
import time
import redis
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from typing import Optional
from med_crew.main import generate_custom_meditation
from pymongo import MongoClient

# --- Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:secret@localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "meditation_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "sessions")

# --- Connections ---
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
mongo_client = MongoClient(MONGO_URL)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

app = FastAPI()

# --- Models ---
class MeditationRequest(BaseModel):
    meditation_type: str = "clarity and peace"  # Keep this as meditation_type for backward compatibility
    duration: int = 8
    difficulty: str = "beginner"
    theme: str = "clarity and peace"

class MeditationStatus(BaseModel):
    job_id: str
    status: str
    result_path: Optional[str] = None
    error: Optional[str] = None

# --- Background Job ---
def run_generation_job(job_id: str, req: MeditationRequest, user_id= None):
    try:
        r.set(f"job:{job_id}:status", "running")
        r.set(f"job:{job_id}:progress", json.dumps({"stage": "starting", "details": "Initializing agents"}))
        import sys
        class DummyFile:
            def write(self, x):
                line = x.strip()
                if line:
                    import re
                    m = re.match(r"\[Agent:(.*?)\] (.*)", line)
                    if m:
                        agent = m.group(1)
                        msg = m.group(2)
                        r.set(f"job:{job_id}:progress", json.dumps({"agent": agent, "message": msg}))
                return None
            def flush(self): return None
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = DummyFile()
        sys.stderr = DummyFile()
        try:
            result = generate_custom_meditation(
                meditation_type=req.meditation_type,
                duration=req.duration,
                difficulty=req.difficulty,
                theme=req.theme
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr



        res_doc = collection.insert_one(dict(**result.model_dump(), user_id=user_id, job_id=job_id))
        r.set(f"job:{job_id}:status", "completed")
        r.set(f"job:{job_id}:progress", json.dumps({"stage": "completed", "details": "Session generated", "session": str(res_doc.inserted_id)}))
    except Exception as e:
        r.set(f"job:{job_id}:status", "failed")
        r.set(f"job:{job_id}:error", str(e))

# --- SSE Generator ---
def sse_event_generator(job_id: str, heartbeat_interval=5):
    last_status = None
    last_progress = None
    last_heartbeat = time.time()

    while True:
        status = r.get(f"job:{job_id}:status")
        progress = r.get(f"job:{job_id}:progress")
        now = time.time()
        event_sent = False

        # Send updates when status or progress changes
        if status != last_status or progress != last_progress:
            data = {"status": status}
            if progress:
                try:
                    data["progress"] = json.loads(progress)
                except Exception:
                    data["progress"] = progress
            if status == "completed":
                data["id"] = job_id
            elif status == "failed":
                data["error"] = r.get(f"job:{job_id}:error")
            yield f"data: {json.dumps(data)}\n\n"
            last_status = status
            last_progress = progress
            event_sent = True

        # Heartbeat: send every heartbeat_interval seconds if no other event was sent
        if not event_sent and now - last_heartbeat >= heartbeat_interval:
            yield f"data: {json.dumps({'status': status or 'running', 'heartbeat': True})}\n\n"
            last_heartbeat = now
            event_sent = True

        if status in ("completed", "failed"):
            break

        time.sleep(1)

# --- API Endpoints ---
@app.post("/generate", response_model=MeditationStatus)
def generate_meditation(req: MeditationRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    r.set(f"job:{job_id}:status", "queued")
    background_tasks.add_task(run_generation_job, job_id, req)
    return MeditationStatus(job_id=job_id, status="queued")

@app.get("/status/{job_id}", response_model=MeditationStatus)
def check_status(job_id: str):
    status = r.get(f"job:{job_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    result_path = r.get(f"job:{job_id}:result_path")
    error = r.get(f"job:{job_id}:error")
    return MeditationStatus(job_id=job_id, status=status, result_path=result_path, error=error)

@app.get("/status/stream/{job_id}")
def stream_status(job_id: str, request: Request, heartbeat_seconds: int = 5):
    """SSE endpoint for job status updates with heartbeat to keep connection alive.

    Args:
        job_id: The ID of the job to stream status updates for
        request: The FastAPI request object
        heartbeat_seconds: How often to send heartbeat events (in seconds)
    """
    return StreamingResponse(sse_event_generator(job_id, heartbeat_interval=heartbeat_seconds),
                             media_type="text/event-stream")

@app.get("/result/{job_id}")
def get_result(job_id: str):
    doc = collection.find_one({"job_id": job_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Result not found or not ready yet")
    # Only return the session object (the validated meditation session)
    if "_id" in doc:
        del doc["_id"]
    return doc
