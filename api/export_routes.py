"""
Export API Routes for AI Interviewer Platform
Provides endpoints for exporting articles in various formats
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import tempfile
import os

from db.database import AsyncSessionLocal
from db.crud import get_article_by_interview_id, get_interview, get_user
from auth.auth_utils import get_current_active_user
from schemas import UserResponse
from api.export_service import export_service

router = APIRouter(prefix="/interviews", tags=["exports"])

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/{job_id}/export/pdf")
async def export_article_pdf(
    job_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export article as PDF
    
    Returns a professionally formatted PDF document containing the article
    with metadata, styling, and branding.
    """
    try:
        # Get interview and verify ownership
        interview = await get_interview(session, job_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if user owns this interview or is admin
        if interview.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the article
        article = await get_article_by_interview_id(session, job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or not ready")
        
        # Get user info for metadata
        user = await get_user(session, interview.user_id) if interview.user_id else None
        
        # Generate PDF
        pdf_buffer = export_service.export_to_pdf(article, interview, user)
        filename = export_service.get_filename(article, 'pdf')
        
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {str(e)}")


@router.get("/{job_id}/export/docx")
async def export_article_docx(
    job_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export article as DOCX
    
    Returns a Microsoft Word document with professional formatting,
    tables for metadata, and proper styling.
    """
    try:
        # Get interview and verify ownership
        interview = await get_interview(session, job_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if user owns this interview or is admin
        if interview.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the article
        article = await get_article_by_interview_id(session, job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or not ready")
        
        # Get user info for metadata
        user = await get_user(session, interview.user_id) if interview.user_id else None
        
        # Generate DOCX
        docx_buffer = export_service.export_to_docx(article, interview, user)
        filename = export_service.get_filename(article, 'docx')
        
        return Response(
            content=docx_buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export DOCX: {str(e)}")


@router.get("/{job_id}/export/markdown")
async def export_article_markdown(
    job_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export article as Markdown
    
    Returns a Markdown formatted document with metadata table
    and proper formatting for version control and web publishing.
    """
    try:
        # Get interview and verify ownership
        interview = await get_interview(session, job_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if user owns this interview or is admin
        if interview.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the article
        article = await get_article_by_interview_id(session, job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or not ready")
        
        # Get user info for metadata
        user = await get_user(session, interview.user_id) if interview.user_id else None
        
        # Generate Markdown
        markdown_content = export_service.export_to_markdown(article, interview, user)
        filename = export_service.get_filename(article, 'md')
        
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/markdown; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export Markdown: {str(e)}")


@router.get("/{job_id}/export/html")
async def export_article_html(
    job_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export article as HTML
    
    Returns a standalone HTML document with embedded CSS styling
    suitable for web viewing or printing.
    """
    try:
        # Get interview and verify ownership
        interview = await get_interview(session, job_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if user owns this interview or is admin
        if interview.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the article
        article = await get_article_by_interview_id(session, job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or not ready")
        
        # Get user info for metadata
        user = await get_user(session, interview.user_id) if interview.user_id else None
        
        # Generate HTML
        html_content = export_service.export_to_html(article, interview, user)
        filename = export_service.get_filename(article, 'html')
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/html; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export HTML: {str(e)}")


@router.get("/{job_id}/export/formats")
async def get_available_export_formats(
    job_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get available export formats for an article
    
    Returns information about available export formats and their descriptions.
    Also validates that the user has access to the article.
    """
    try:
        # Get interview and verify ownership
        interview = await get_interview(session, job_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if user owns this interview or is admin
        if interview.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get the article
        article = await get_article_by_interview_id(session, job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found or not ready")
        
        formats = {
            "available_formats": [
                {
                    "format": "pdf",
                    "name": "PDF Document",
                    "description": "Professional PDF with formatting, perfect for printing and sharing",
                    "endpoint": f"/interviews/{job_id}/export/pdf",
                    "mime_type": "application/pdf",
                    "extension": "pdf"
                },
                {
                    "format": "docx",
                    "name": "Microsoft Word Document",
                    "description": "Editable Word document with tables and styling",
                    "endpoint": f"/interviews/{job_id}/export/docx",
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "extension": "docx"
                },
                {
                    "format": "markdown",
                    "name": "Markdown Document",
                    "description": "Plain text format perfect for version control and web publishing",
                    "endpoint": f"/interviews/{job_id}/export/markdown",
                    "mime_type": "text/markdown",
                    "extension": "md"
                },
                {
                    "format": "html",
                    "name": "HTML Document",
                    "description": "Standalone web page with embedded styling",
                    "endpoint": f"/interviews/{job_id}/export/html",
                    "mime_type": "text/html",
                    "extension": "html"
                }
            ],
            "article_info": {
                "title": article.title,
                "version": article.version,
                "created_at": article.created_at.isoformat(),
                "interview_topic": interview.topic,
                "target_audience": interview.target_audience
            }
        }
        
        return formats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export formats: {str(e)}")


# Batch export functionality
@router.post("/batch/export/{format_type}")
async def batch_export_articles(
    format_type: str,
    interview_ids: list[int] = Query(..., description="List of interview IDs to export"),
    current_user: UserResponse = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export multiple articles in a single request
    
    Creates a zip file containing all requested articles in the specified format.
    Only exports articles that the user owns or has admin access to.
    """
    try:
        import zipfile
        import tempfile
        
        # Validate format type
        if format_type not in ["pdf", "docx", "markdown", "html"]:
            raise HTTPException(status_code=400, detail="Invalid format type")
        
        if len(interview_ids) > 20:  # Limit batch size
            raise HTTPException(status_code=400, detail="Too many articles requested (max 20)")
        
        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"articles_batch_{format_type}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            exported_count = 0
            
            for job_id in interview_ids:
                try:
                    # Get interview and verify ownership
                    interview = await get_interview(session, job_id)
                    if not interview:
                        continue  # Skip missing interviews
                    
                    # Check if user owns this interview or is admin
                    if interview.user_id != current_user.id and current_user.role != "admin":
                        continue  # Skip unauthorized interviews
                    
                    # Get the article
                    article = await get_article_by_interview_id(session, job_id)
                    if not article:
                        continue  # Skip missing articles
                    
                    # Get user info
                    user = await get_user(session, interview.user_id) if interview.user_id else None
                    
                    # Generate content based on format
                    filename = export_service.get_filename(article, format_type)
                    
                    if format_type == "pdf":
                        buffer = export_service.export_to_pdf(article, interview, user)
                        zip_file.writestr(filename, buffer.getvalue())
                    elif format_type == "docx":
                        buffer = export_service.export_to_docx(article, interview, user)
                        zip_file.writestr(filename, buffer.getvalue())
                    elif format_type == "markdown":
                        content = export_service.export_to_markdown(article, interview, user)
                        zip_file.writestr(filename, content.encode('utf-8'))
                    elif format_type == "html":
                        content = export_service.export_to_html(article, interview, user)
                        zip_file.writestr(filename, content.encode('utf-8'))
                    
                    exported_count += 1
                    
                except Exception as e:
                    # Log error but continue with other articles
                    print(f"Error exporting article {job_id}: {e}")
                    continue
        
        if exported_count == 0:
            raise HTTPException(status_code=404, detail="No articles could be exported")
        
        # Return the zip file
        return FileResponse(
            path=zip_path,
            filename=f"articles_batch_{format_type}.zip",
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=articles_batch_{format_type}.zip"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create batch export: {str(e)}") 