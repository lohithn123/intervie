from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Interview, Article

async def create_interview(session: AsyncSession, topic: str, target_audience: str) -> Interview:
    interview = Interview(topic=topic, target_audience=target_audience)
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
