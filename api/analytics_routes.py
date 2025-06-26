from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from db.database import AsyncSessionLocal
from db.crud import get_dashboard_data, get_user_analytics, track_api_usage, update_user_engagement
from schemas import AnalyticsDashboardData, APIUsageMetricsCreate, UserEngagementMetricsCreate, UserResponse
from auth.auth_utils import get_current_user, require_admin

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/dashboard", response_model=AnalyticsDashboardData)
async def get_analytics_dashboard(
    current_user: UserResponse = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard data (Admin only)
    
    Returns:
    - User activity metrics
    - Interview completion rates
    - Popular topics and templates
    - API usage and costs
    - Performance metrics
    """
    try:
        dashboard_data = await get_dashboard_data(session)
        return AnalyticsDashboardData(**dashboard_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics data: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_analytics_data(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get analytics data for a specific user
    
    Users can only view their own analytics unless they're admin
    """
    # Check if user can access this data
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        user_analytics = await get_user_analytics(session, user_id)
        return user_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user analytics: {str(e)}")


@router.get("/user/me")
async def get_my_analytics(
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get analytics data for the current user"""
    try:
        user_analytics = await get_user_analytics(session, current_user.id)
        return user_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")


@router.post("/api-usage")
async def log_api_usage(
    usage_data: APIUsageMetricsCreate,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Log API usage for cost tracking"""
    try:
        usage_record = await track_api_usage(
            session=session,
            service_type=usage_data.service_type,
            operation=usage_data.operation,
            user_id=current_user.id,
            tokens_used=usage_data.tokens_used,
            characters_processed=usage_data.characters_processed,
            cost_usd=usage_data.cost_usd
        )
        return {"message": "API usage logged", "id": usage_record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log API usage: {str(e)}")


@router.post("/user-engagement")
async def log_user_engagement(
    engagement_data: UserEngagementMetricsCreate,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Log user engagement metrics"""
    try:
        # Only allow users to log their own engagement or admins to log any
        if current_user.role != "admin" and current_user.id != engagement_data.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        engagement_record = await update_user_engagement(
            session=session,
            user_id=engagement_data.user_id,
            date=engagement_data.date,
            interviews_started=engagement_data.interviews_started,
            interviews_completed=engagement_data.interviews_completed,
            session_time=engagement_data.total_session_time,
            articles_generated=engagement_data.articles_generated,
            login_count=engagement_data.login_count
        )
        return {"message": "User engagement logged", "id": engagement_record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log user engagement: {str(e)}")


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    current_user: UserResponse = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get a quick analytics summary for the specified time period"""
    try:
        dashboard_data = await get_dashboard_data(session)
        
        # Create a simplified summary
        summary = {
            "period_days": days,
            "total_users": dashboard_data["total_users"],
            "active_users_today": dashboard_data["active_users_today"],
            "total_interviews": dashboard_data["total_interviews"],
            "completion_rate": dashboard_data["completion_rate"],
            "total_api_cost": dashboard_data["total_api_cost"],
            "top_topics": dashboard_data["popular_topics"][:5],
            "top_templates": dashboard_data["popular_templates"][:5]
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics summary: {str(e)}")


@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date for data export"),
    end_date: Optional[datetime] = Query(None, description="End date for data export"),
    current_user: UserResponse = Depends(require_admin),
    session: AsyncSession = Depends(get_db)
):
    """Export analytics data in JSON or CSV format (Admin only)"""
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        dashboard_data = await get_dashboard_data(session)
        
        if format == "json":
            return {
                "export_date": datetime.utcnow().isoformat(),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "data": dashboard_data
            }
        else:
            # CSV format would require additional processing
            # For now, return JSON with a note
            return {
                "message": "CSV export not yet implemented",
                "data": dashboard_data
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}") 