from pydantic import BaseModel
from typing import List

class InterviewMessage(BaseModel):
    speaker: str
    content: str

class InterviewTranscript(BaseModel):
    messages: List[InterviewMessage]

class ArticleDraft(BaseModel):
    title: str
    content: str
    version: int

class EditorFeedback(BaseModel):
    is_approved: bool
    critiques: List[str] 