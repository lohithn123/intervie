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