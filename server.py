from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from db.database import AsyncSessionLocal
from db import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
from api.agents import writer_agent, editor_agent, mock_interview
from schemas import InterviewTranscript, ArticleDraft

app = FastAPI()

# In-memory job status tracking (for demo)
job_status = {}

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Pydantic models for API
class InterviewStartRequest(BaseModel):
    topic: str
    target_audience: str

class InterviewStartResponse(BaseModel):
    job_id: int
    status: str = "started"

class InterviewStatusResponse(BaseModel):
    job_id: int
    status: str
    message: Optional[str] = None

class ArticleResponse(BaseModel):
    title: str
    content: str
    version: int

async def run_workflow(interview_id: int, topic: str, target_audience: str):
    job_status[interview_id] = "running"
    # Step 1: Mock interview transcript
    transcript: InterviewTranscript = mock_interview(None, topic)
    # Step 2: Writer/Editor loop
    version = 1
    draft = None
    while True:
        draft_result = await writer_agent.run(transcript=transcript, target_audience=target_audience, version=version)
        draft: ArticleDraft = draft_result.output
        feedback_result = await editor_agent.run(draft=draft)
        feedback = feedback_result.output
        if feedback.is_approved:
            break
        version += 1
    # Step 3: Save transcript and article to DB
    async with AsyncSessionLocal() as session:
        await crud.update_interview_transcript(session, interview_id, transcript.json())
        await crud.create_article(session, interview_id, draft.title, draft.content, draft.version)
    job_status[interview_id] = "completed"

@app.post("/interviews/start", response_model=InterviewStartResponse)
async def start_interview(
    req: InterviewStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    interview = await crud.create_interview(db, req.topic, req.target_audience)
    job_status[interview.id] = "pending"
    background_tasks.add_task(run_workflow, interview.id, req.topic, req.target_audience)
    return InterviewStartResponse(job_id=interview.id)

@app.get("/interviews/{job_id}/status", response_model=InterviewStatusResponse)
async def get_interview_status(job_id: int):
    status = job_status.get(job_id, "unknown")
    return InterviewStatusResponse(job_id=job_id, status=status)

@app.get("/interviews/{job_id}/result", response_model=ArticleResponse)
async def get_interview_result(job_id: int, db: AsyncSession = Depends(get_db)):
    article = await crud.get_article_by_interview_id(db, job_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not ready.")
    return ArticleResponse(title=article.title, content=article.content, version=article.version)

@app.websocket("/interviews/stream/{job_id}")
async def interview_audio_stream(websocket: WebSocket, job_id: int):
    await websocket.accept()
    try:
        while True:
            # Receive audio chunk from client
            audio_chunk = await websocket.receive_bytes()
            # TODO: Transcribe audio_chunk using ElevenLabs STT
            # transcript = await transcribe_audio(audio_chunk)
            # TODO: Pass transcript to InterviewerAgent and get response
            # TODO: Synthesize response using ElevenLabs TTS
            # audio_response = await synthesize_speech(response_text)
            # For now, just echo back the received audio
            await websocket.send_bytes(audio_chunk)
    except WebSocketDisconnect:
        pass

@app.get("/")
def root():
    return {"message": "AI Interviewer API is running."} 