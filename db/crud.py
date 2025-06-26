from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_, desc
from .models import Interview, Article, User, InterviewTemplate, InterviewSession, APIUsageMetrics, UserEngagementMetrics, SystemMetrics, EditedTranscript
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

# User CRUD operations
async def create_user(session: AsyncSession, email: str, username: str, hashed_password: str, full_name: Optional[str] = None) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def update_user(session: AsyncSession, user_id: int, **kwargs) -> Optional[User]:
    user = await get_user(session, user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
    return user

async def get_user_interviews(session: AsyncSession, user_id: int, limit: int = 20, offset: int = 0):
    result = await session.execute(
        select(Interview)
        .where(Interview.user_id == user_id)
        .options(selectinload(Interview.article))
        .order_by(Interview.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

# Updated Interview CRUD operations
async def create_interview(
    session: AsyncSession, 
    topic: str, 
    target_audience: str, 
    user_id: Optional[int] = None,
    template_id: Optional[int] = None
) -> Interview:
    interview = Interview(
        topic=topic, 
        target_audience=target_audience,
        user_id=user_id,
        template_id=template_id
    )
    session.add(interview)
    await session.commit()
    await session.refresh(interview)
    return interview

async def get_interview(session: AsyncSession, interview_id: int) -> Interview:
    result = await session.execute(select(Interview).where(Interview.id == interview_id))
    return result.scalar_one_or_none()

async def update_interview_transcript(session: AsyncSession, interview_id: int, transcript: str) -> Interview:
    interview = await get_interview(session, interview_id)
    if interview:
        interview.transcript = transcript
        await session.commit()
        await session.refresh(interview)
    return interview

async def create_article(session: AsyncSession, interview_id: int, title: str, content: str, version: int) -> Article:
    article = Article(interview_id=interview_id, title=title, content=content, version=version)
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article

async def get_article_by_interview_id(session: AsyncSession, interview_id: int) -> Article:
    result = await session.execute(select(Article).where(Article.interview_id == interview_id))
    return result.scalar_one_or_none()


# Interview Template CRUD operations
async def create_template(
    session: AsyncSession,
    name: str,
    domain: str,
    initial_questions: str,  # JSON string
    created_by: int,
    description: Optional[str] = None,
    follow_up_patterns: Optional[str] = None,  # JSON string
    target_style: Optional[str] = "conversational",
    target_tone: Optional[str] = "professional",
    voice_persona: Optional[str] = "neutral"
) -> InterviewTemplate:
    """Create a new interview template"""
    template = InterviewTemplate(
        name=name,
        domain=domain,
        description=description,
        initial_questions=initial_questions,
        follow_up_patterns=follow_up_patterns,
        target_style=target_style,
        target_tone=target_tone,
        voice_persona=voice_persona,
        created_by=created_by
    )
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


async def get_template(session: AsyncSession, template_id: int) -> Optional[InterviewTemplate]:
    """Get template by ID"""
    query = select(InterviewTemplate).where(InterviewTemplate.id == template_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_templates(
    session: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    domain: Optional[str] = None,
    is_active: bool = True
) -> List[InterviewTemplate]:
    """Get list of templates with optional filtering"""
    query = select(InterviewTemplate)
    
    if domain:
        query = query.where(InterviewTemplate.domain == domain)
    if is_active is not None:
        query = query.where(InterviewTemplate.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def update_template(
    session: AsyncSession,
    template_id: int,
    update_data: dict
) -> Optional[InterviewTemplate]:
    """Update a template"""
    template = await get_template(session, template_id)
    if not template:
        return None
    
    for field, value in update_data.items():
        if hasattr(template, field) and value is not None:
            setattr(template, field, value)
    
    await session.commit()
    await session.refresh(template)
    return template


async def delete_template(session: AsyncSession, template_id: int) -> bool:
    """Delete a template (soft delete by setting is_active=False)"""
    template = await get_template(session, template_id)
    if not template:
        return False
    
    template.is_active = False
    await session.commit()
    return True


# Analytics CRUD operations

async def create_interview_session(
    session: AsyncSession,
    interview_id: int,
    user_id: Optional[int] = None,
    started_at: datetime = None
) -> InterviewSession:
    """Create a new interview session tracking record"""
    if started_at is None:
        started_at = datetime.utcnow()
    
    session_record = InterviewSession(
        interview_id=interview_id,
        user_id=user_id,
        started_at=started_at
    )
    session.add(session_record)
    await session.commit()
    await session.refresh(session_record)
    return session_record


async def update_interview_session(
    session: AsyncSession,
    session_id: int,
    **kwargs
) -> Optional[InterviewSession]:
    """Update interview session with completion data"""
    query = select(InterviewSession).where(InterviewSession.id == session_id)
    result = await session.execute(query)
    session_record = result.scalar_one_or_none()
    
    if session_record:
        for key, value in kwargs.items():
            if hasattr(session_record, key):
                setattr(session_record, key, value)
        await session.commit()
        await session.refresh(session_record)
    
    return session_record


async def track_api_usage(
    session: AsyncSession,
    service_type: str,
    operation: str,
    user_id: Optional[int] = None,
    tokens_used: Optional[int] = None,
    characters_processed: Optional[int] = None,
    cost_usd: Optional[float] = None
) -> APIUsageMetrics:
    """Track API usage for cost analysis"""
    usage_record = APIUsageMetrics(
        user_id=user_id,
        service_type=service_type,
        operation=operation,
        tokens_used=tokens_used,
        characters_processed=characters_processed,
        cost_usd=cost_usd
    )
    session.add(usage_record)
    await session.commit()
    await session.refresh(usage_record)
    return usage_record


async def update_user_engagement(
    session: AsyncSession,
    user_id: int,
    date: datetime,
    interviews_started: int = 0,
    interviews_completed: int = 0,
    session_time: int = 0,
    articles_generated: int = 0,
    template_id: Optional[int] = None,
    login_count: int = 0
) -> UserEngagementMetrics:
    """Update daily user engagement metrics"""
    # Check if record exists for this user and date
    query = select(UserEngagementMetrics).where(
        and_(
            UserEngagementMetrics.user_id == user_id,
            func.date(UserEngagementMetrics.date) == date.date()
        )
    )
    result = await session.execute(query)
    engagement = result.scalar_one_or_none()
    
    if engagement:
        # Update existing record
        engagement.interviews_started += interviews_started
        engagement.interviews_completed += interviews_completed
        engagement.total_session_time += session_time
        engagement.articles_generated += articles_generated
        engagement.login_count += login_count
        
        if template_id:
            templates = engagement.templates_used.split(',') if engagement.templates_used else []
            if str(template_id) not in templates:
                templates.append(str(template_id))
                engagement.templates_used = ','.join(templates)
    else:
        # Create new record
        engagement = UserEngagementMetrics(
            user_id=user_id,
            date=date,
            interviews_started=interviews_started,
            interviews_completed=interviews_completed,
            total_session_time=session_time,
            articles_generated=articles_generated,
            templates_used=str(template_id) if template_id else None,
            login_count=login_count
        )
        session.add(engagement)
    
    await session.commit()
    await session.refresh(engagement)
    return engagement


async def get_dashboard_data(session: AsyncSession) -> Dict[str, Any]:
    """Get comprehensive analytics data for dashboard"""
    now = datetime.utcnow()
    today = now.date()
    week_ago = today - timedelta(days=7)
    
    # Basic counts
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    total_interviews_result = await session.execute(select(func.count(Interview.id)))
    total_interviews = total_interviews_result.scalar()
    
    successful_interviews_result = await session.execute(
        select(func.count(Interview.id)).where(Interview.status == 'completed')
    )
    successful_interviews = successful_interviews_result.scalar()
    
    # Active users today
    active_users_today_result = await session.execute(
        select(func.count(func.distinct(UserEngagementMetrics.user_id)))
        .where(func.date(UserEngagementMetrics.date) == today)
    )
    active_users_today = active_users_today_result.scalar() or 0
    
    # Recent interviews
    recent_interviews_result = await session.execute(
        select(Interview)
        .where(Interview.created_at >= datetime.combine(week_ago, datetime.min.time()))
        .order_by(Interview.created_at.desc())
        .limit(50)
    )
    recent_interviews = recent_interviews_result.scalars().all()
    
    # Popular topics
    popular_topics_result = await session.execute(
        select(Interview.topic, func.count(Interview.topic).label('count'))
        .group_by(Interview.topic)
        .order_by(desc('count'))
        .limit(10)
    )
    popular_topics = [{"topic": row[0], "count": row[1]} for row in popular_topics_result.fetchall()]
    
    # Popular templates
    popular_templates_result = await session.execute(
        select(InterviewTemplate.name, func.count(Interview.template_id).label('count'))
        .join(Interview, Interview.template_id == InterviewTemplate.id)
        .group_by(InterviewTemplate.name)
        .order_by(desc('count'))
        .limit(10)
    )
    popular_templates = [{"name": row[0], "count": row[1]} for row in popular_templates_result.fetchall()]
    
    # Average metrics
    avg_duration_result = await session.execute(
        select(func.avg(Interview.duration_seconds))
        .where(Interview.duration_seconds.isnot(None))
    )
    avg_duration = avg_duration_result.scalar()
    
    avg_iterations_result = await session.execute(
        select(func.avg(Article.editor_iterations))
    )
    avg_iterations = avg_iterations_result.scalar()
    
    # API costs
    total_cost_result = await session.execute(
        select(func.sum(APIUsageMetrics.cost_usd))
    )
    total_cost = total_cost_result.scalar() or 0.0
    
    # Cost breakdown by service
    cost_breakdown_result = await session.execute(
        select(APIUsageMetrics.service_type, func.sum(APIUsageMetrics.cost_usd))
        .group_by(APIUsageMetrics.service_type)
    )
    cost_breakdown = {row[0]: row[1] for row in cost_breakdown_result.fetchall()}
    
    # User activity (last 7 days)
    user_activity_result = await session.execute(
        select(
            func.date(UserEngagementMetrics.date).label('date'),
            func.sum(UserEngagementMetrics.interviews_started).label('interviews'),
            func.count(func.distinct(UserEngagementMetrics.user_id)).label('active_users')
        )
        .where(UserEngagementMetrics.date >= datetime.combine(week_ago, datetime.min.time()))
        .group_by(func.date(UserEngagementMetrics.date))
        .order_by('date')
    )
    user_activity = [
        {
            "date": row[0].isoformat(),
            "interviews": row[1] or 0,
            "active_users": row[2] or 0
        }
        for row in user_activity_result.fetchall()
    ]
    
    # Calculate completion rate
    completion_rate = (successful_interviews / total_interviews * 100) if total_interviews > 0 else 0
    
    # Prepare interviews for last 7 days
    interviews_last_7_days = [
        {
            "id": interview.id,
            "topic": interview.topic,
            "status": interview.status,
            "created_at": interview.created_at.isoformat(),
            "duration": interview.duration_seconds
        }
        for interview in recent_interviews
    ]
    
    return {
        "total_users": total_users,
        "active_users_today": active_users_today,
        "total_interviews": total_interviews,
        "successful_interviews": successful_interviews,
        "completion_rate": round(completion_rate, 2),
        "interviews_last_7_days": interviews_last_7_days,
        "popular_topics": popular_topics,
        "popular_templates": popular_templates,
        "average_interview_duration": avg_duration,
        "average_editor_iterations": avg_iterations,
        "transcript_quality_score": None,  # Would need implementation
        "total_api_cost": total_cost,
        "cost_breakdown": cost_breakdown,
        "user_activity": user_activity,
        "retention_metrics": {}  # Would need more complex calculation
    }


async def get_user_analytics(session: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get analytics specific to a user"""
    # User's interviews
    user_interviews_result = await session.execute(
        select(Interview).where(Interview.user_id == user_id)
    )
    user_interviews = user_interviews_result.scalars().all()
    
    # User engagement over time
    engagement_result = await session.execute(
        select(UserEngagementMetrics)
        .where(UserEngagementMetrics.user_id == user_id)
        .order_by(UserEngagementMetrics.date.desc())
        .limit(30)
    )
    engagement_history = engagement_result.scalars().all()
    
    # User's API usage costs
    user_costs_result = await session.execute(
        select(func.sum(APIUsageMetrics.cost_usd))
        .where(APIUsageMetrics.user_id == user_id)
    )
    user_total_cost = user_costs_result.scalar() or 0.0
    
    return {
        "total_interviews": len(user_interviews),
        "completed_interviews": len([i for i in user_interviews if i.status == 'completed']),
        "total_cost": user_total_cost,
        "engagement_history": [
            {
                "date": eng.date.isoformat(),
                "interviews": eng.interviews_completed,
                "session_time": eng.total_session_time
            }
            for eng in engagement_history
        ]
    }


# Edited Transcripts CRUD
async def save_edited_transcript(
    session: AsyncSession,
    interview_id: int,
    user_id: int,
    messages: list,
    edit_notes: str = None
) -> EditedTranscript:
    """Save or update an edited transcript"""
    import json
    
    # Check if transcript already exists
    stmt = select(EditedTranscript).where(
        and_(
            EditedTranscript.interview_id == interview_id,
            EditedTranscript.user_id == user_id
        )
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing transcript
        existing.messages = json.dumps(messages)
        existing.edit_notes = edit_notes
        existing.updated_at = func.now()
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        # Create new transcript
        transcript = EditedTranscript(
            interview_id=interview_id,
            user_id=user_id,
            messages=json.dumps(messages),
            edit_notes=edit_notes
        )
        session.add(transcript)
        await session.commit()
        await session.refresh(transcript)
        return transcript


async def get_edited_transcript(
    session: AsyncSession,
    interview_id: int,
    user_id: int
) -> Optional[EditedTranscript]:
    """Get edited transcript for an interview by a specific user"""
    stmt = select(EditedTranscript).where(
        and_(
            EditedTranscript.interview_id == interview_id,
            EditedTranscript.user_id == user_id
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_edited_transcripts(
    session: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[EditedTranscript]:
    """Get all edited transcripts for a user"""
    stmt = select(EditedTranscript).where(
        EditedTranscript.user_id == user_id
    ).offset(skip).limit(limit).order_by(EditedTranscript.updated_at.desc())
    
    result = await session.execute(stmt)
    return result.scalars().all()
