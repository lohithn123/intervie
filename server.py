from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from db.database import AsyncSessionLocal
from db import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

app = FastAPI()

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

@app.post("/interviews/start", response_model=InterviewStartResponse)
async def start_interview(
    req: InterviewStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    interview = await crud.create_interview(db, req.topic, req.target_audience)
    # TODO: Trigger agent workflow in background
    # background_tasks.add_task(run_workflow, interview.id)
    return InterviewStartResponse(job_id=interview.id)

@app.get("/interviews/{job_id}/status", response_model=InterviewStatusResponse)
async def get_interview_status(job_id: int):
    # TODO: Implement real status tracking
    return InterviewStatusResponse(job_id=job_id, status="pending", message="Workflow in progress.")

@app.get("/interviews/{job_id}/result", response_model=ArticleResponse)
async def get_interview_result(job_id: int, db: AsyncSession = Depends(get_db)):
    article = await crud.get_article_by_interview_id(db, job_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not ready.")
    return ArticleResponse(title=article.title, content=article.content, version=article.version)

@app.get("/")
def root():
    return {"message": "AI Interviewer API is running."} 