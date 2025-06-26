from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .models import Interview, Article, User
from typing import Optional

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
async def create_interview(session: AsyncSession, topic: str, target_audience: str, user_id: Optional[int] = None) -> Interview:
    interview = Interview(
        topic=topic, 
        target_audience=target_audience,
        user_id=user_id
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
