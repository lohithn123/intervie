from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

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

# Authentication Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
class UserInDB(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
class UserResponse(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    
class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str


# Interview Templates
class TemplateBase(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None
    initial_questions: List[str]
    follow_up_patterns: Optional[dict] = None
    target_style: Optional[str] = "conversational"
    target_tone: Optional[str] = "professional"
    voice_persona: Optional[str] = "neutral"


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    initial_questions: Optional[List[str]] = None
    follow_up_patterns: Optional[dict] = None
    target_style: Optional[str] = None
    target_tone: Optional[str] = None
    voice_persona: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class InterviewSessionBase(BaseModel):
    interview_id: int
    user_id: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    questions_asked: int = 0
    words_spoken: int = 0
    completion_status: Optional[str] = None
    transcript_quality_score: Optional[float] = None


class InterviewSessionCreate(InterviewSessionBase):
    pass


class InterviewSessionResponse(InterviewSessionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIUsageMetricsBase(BaseModel):
    user_id: Optional[int] = None
    service_type: str
    operation: str
    tokens_used: Optional[int] = None
    characters_processed: Optional[int] = None
    cost_usd: Optional[float] = None


class APIUsageMetricsCreate(APIUsageMetricsBase):
    pass


class APIUsageMetricsResponse(APIUsageMetricsBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class UserEngagementMetricsBase(BaseModel):
    user_id: int
    date: datetime
    interviews_started: int = 0
    interviews_completed: int = 0
    total_session_time: int = 0
    articles_generated: int = 0
    templates_used: Optional[str] = None
    login_count: int = 0


class UserEngagementMetricsCreate(UserEngagementMetricsBase):
    pass


class UserEngagementMetricsResponse(UserEngagementMetricsBase):
    id: int
    
    class Config:
        from_attributes = True


class SystemMetricsBase(BaseModel):
    date: datetime
    active_users: int = 0
    total_interviews: int = 0
    successful_interviews: int = 0
    failed_interviews: int = 0
    average_interview_duration: Optional[float] = None
    average_editor_iterations: Optional[float] = None
    total_api_cost: float = 0.0
    popular_topics: Optional[str] = None
    popular_templates: Optional[str] = None


class SystemMetricsCreate(SystemMetricsBase):
    pass


class SystemMetricsResponse(SystemMetricsBase):
    id: int
    
    class Config:
        from_attributes = True


class AnalyticsDashboardData(BaseModel):
    """Combined analytics data for dashboard display"""
    # Overview metrics
    total_users: int
    active_users_today: int
    total_interviews: int
    successful_interviews: int
    completion_rate: float
    
    # Recent activity
    interviews_last_7_days: List[dict]
    popular_topics: List[dict]
    popular_templates: List[dict]
    
    # Performance metrics
    average_interview_duration: Optional[float]
    average_editor_iterations: Optional[float]
    transcript_quality_score: Optional[float]
    
    # Cost analysis
    total_api_cost: float
    cost_breakdown: dict
    
    # User engagement
    user_activity: List[dict]
    retention_metrics: dict 