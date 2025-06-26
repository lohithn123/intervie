from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from db.database import AsyncSessionLocal
from db import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
import json
from api.agents import writer_agent, editor_agent, mock_interview, WriterContext, EditorContext
from api.interview_handler import handle_interview_audio_stream
from api.auth_routes import router as auth_router
from api.template_routes import router as template_router
from api.analytics_routes import router as analytics_router
from api.export_routes import router as export_router
from api.transcript_routes import router as transcript_router
from auth.auth_utils import get_current_active_user
from schemas import InterviewTranscript, ArticleDraft
from db.models import User

app = FastAPI(title="AI Interviewer Platform", version="2.0.0")

# Include authentication routes
app.include_router(auth_router)

# Include template routes
app.include_router(template_router)

# Include analytics routes
app.include_router(analytics_router)

# Include export routes
app.include_router(export_router)
app.include_router(transcript_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    mode: str = "text"  # "text" or "voice"
    template_id: Optional[int] = None  # Optional template to use

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

async def run_workflow(interview_id: int, topic: str, target_audience: str, transcript: Optional[InterviewTranscript] = None):
    job_status[interview_id] = "running"
    
    try:
        # Step 1: Use provided transcript or generate mock interview
        if transcript is None:
            transcript = mock_interview(topic)
        
        # Step 2: Writer/Editor loop
        version = 1
        draft = None
        editor_feedback = []
        
        while True:
            # Create writer context
            writer_ctx = WriterContext(
                transcript=transcript,
                target_audience=target_audience,
                version=version,
                editor_feedback=editor_feedback
            )
            
            # Generate article draft
            draft_result = await writer_agent.run(writer_ctx)
            draft = draft_result.data
            
            # Create editor context
            editor_ctx = EditorContext(draft=draft)
            
            # Get editor feedback
            feedback_result = await editor_agent.run(editor_ctx)
            feedback = feedback_result.data
            
            if feedback.is_approved:
                break
            
            # Prepare for next iteration
            editor_feedback = feedback.critiques
            version += 1
            
            # Safety check to prevent infinite loops
            if version > 5:
                break
        
        # Step 3: Save transcript and article to DB
        async with AsyncSessionLocal() as session:
            await crud.update_interview_transcript(session, interview_id, transcript.model_dump_json())
            await crud.create_article(session, interview_id, draft.title, draft.content, draft.version)
        
        job_status[interview_id] = "completed"
        
    except Exception as e:
        job_status[interview_id] = f"failed: {str(e)}"
        raise

@app.post("/interviews/start", response_model=InterviewStartResponse)
async def start_interview(
    req: InterviewStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Require authentication
):
    interview = await crud.create_interview(
        db, 
        req.topic, 
        req.target_audience,
        user_id=current_user.id,  # Associate with current user
        template_id=req.template_id  # Associate with template if provided
    )
    job_status[interview.id] = "pending"
    
    if req.mode == "text":
        # Traditional text-based workflow
        background_tasks.add_task(run_workflow, interview.id, req.topic, req.target_audience)
    else:
        # Voice mode - will be handled via WebSocket
        job_status[interview.id] = "waiting_for_voice"
    
    return InterviewStartResponse(job_id=interview.id)

@app.get("/interviews/{job_id}/status", response_model=InterviewStatusResponse)
async def get_interview_status(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify user owns this interview
    interview = await crud.get_interview(db, job_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    status = job_status.get(job_id, "unknown")
    return InterviewStatusResponse(job_id=job_id, status=status)

@app.get("/interviews/{job_id}/result", response_model=ArticleResponse)
async def get_interview_result(
    job_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify user owns this interview
    interview = await crud.get_interview(db, job_id)
    if not interview or interview.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    article = await crud.get_article_by_interview_id(db, job_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not ready.")
    return ArticleResponse(title=article.title, content=article.content, version=article.version)

# New endpoint for user's interview history
@app.get("/interviews/my/history")
async def get_my_interviews(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's interview history."""
    interviews = await crud.get_user_interviews(db, current_user.id, limit, offset)
    return {
        "interviews": [
            {
                "id": interview.id,
                "topic": interview.topic,
                "target_audience": interview.target_audience,
                "status": interview.status,
                "created_at": interview.created_at,
                "has_article": bool(interview.article)
            }
            for interview in interviews
        ],
        "user_id": current_user.id,
        "limit": limit,
        "offset": offset
    }

@app.websocket("/interviews/stream/{job_id}")
async def interview_audio_stream(websocket: WebSocket, job_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    
    # Get interview details
    interview = await crud.get_interview(db, job_id)
    if not interview:
        await websocket.close(code=4004, reason="Interview not found")
        return
    
    job_status[job_id] = "interviewing"
    
    try:
        # Load template if associated with interview
        template_data = None
        if interview.template_id:
            template = await crud.get_template(db, interview.template_id)
            if template:
                template_data = {
                    "name": template.name,
                    "domain": template.domain,
                    "initial_questions": json.loads(template.initial_questions),
                    "follow_up_patterns": json.loads(template.follow_up_patterns) if template.follow_up_patterns else {},
                    "target_style": template.target_style,
                    "target_tone": template.target_tone,
                    "voice_persona": template.voice_persona
                }
        
        # Conduct the voice interview
        transcript = await handle_interview_audio_stream(
            websocket=websocket,
            interview_id=job_id,
            topic=interview.topic,
            target_audience=interview.target_audience,
            template=template_data
        )
        
        # Close the WebSocket
        await websocket.close(code=1000, reason="Interview completed")
        
        # Run the article generation workflow with the real transcript
        await run_workflow(job_id, interview.topic, interview.target_audience, transcript)
        
    except WebSocketDisconnect:
        job_status[job_id] = "disconnected"
    except Exception as e:
        job_status[job_id] = f"error: {str(e)}"
        await websocket.close(code=4000, reason=str(e))

@app.get("/")
def root():
    return FileResponse("static/interview_client_auth.html")

@app.get("/admin/templates")
def template_admin():
    return FileResponse("static/template_admin.html")

@app.get("/admin/analytics")
def analytics_dashboard():
    return FileResponse("static/analytics_dashboard.html") 