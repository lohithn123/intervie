from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, guest
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for backward compatibility
    template_id = Column(Integer, ForeignKey("interview_templates.id"), nullable=True)
    topic = Column(String(255), nullable=False)
    target_audience = Column(String(255), nullable=False)
    transcript = Column(Text)
    status = Column(String(50), default="pending")  # pending, interviewing, completed, failed
    duration_seconds = Column(Integer)  # Interview duration for analytics
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    template = relationship("InterviewTemplate", back_populates="interviews")
    article = relationship("Article", back_populates="interview", uselist=False, cascade="all, delete-orphan")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    editor_iterations = Column(Integer, default=0)  # Track quality for analytics
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="article")


class InterviewTemplate(Base):
    __tablename__ = "interview_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    domain = Column(String(100), nullable=False)  # journalism, research, marketing, etc.
    description = Column(Text)
    initial_questions = Column(Text, nullable=False)  # JSON array of questions
    follow_up_patterns = Column(Text)  # JSON object with patterns
    target_style = Column(String(100))  # formal, conversational, academic, etc.
    target_tone = Column(String(100))  # professional, friendly, investigative, etc.
    voice_persona = Column(String(100))  # voice characteristics for TTS
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    interviews = relationship("Interview", back_populates="template")
