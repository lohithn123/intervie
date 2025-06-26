"""Interview Template API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from db.database import AsyncSessionLocal
from db import crud
from schemas import TemplateCreate, TemplateUpdate, TemplateResponse
from auth.auth_utils import get_current_user, require_admin

router = APIRouter(prefix="/templates", tags=["Templates"])

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview template (admin only)."""
    # Convert lists/dicts to JSON strings for storage
    initial_questions_json = json.dumps(template_data.initial_questions)
    follow_up_patterns_json = json.dumps(template_data.follow_up_patterns) if template_data.follow_up_patterns else None
    
    template = await crud.create_template(
        db,
        name=template_data.name,
        domain=template_data.domain,
        initial_questions=initial_questions_json,
        created_by=current_user.id,
        description=template_data.description,
        follow_up_patterns=follow_up_patterns_json,
        target_style=template_data.target_style,
        target_tone=template_data.target_tone,
        voice_persona=template_data.voice_persona
    )
    
    # Convert back to response format
    return TemplateResponse(
        id=template.id,
        name=template.name,
        domain=template.domain,
        description=template.description,
        initial_questions=json.loads(template.initial_questions),
        follow_up_patterns=json.loads(template.follow_up_patterns) if template.follow_up_patterns else None,
        target_style=template.target_style,
        target_tone=template.target_tone,
        voice_persona=template.voice_persona,
        is_active=template.is_active,
        created_by=template.created_by,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    domain: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List available interview templates."""
    templates = await crud.get_templates(db, skip=skip, limit=limit, domain=domain)
    
    # Convert to response format
    return [
        TemplateResponse(
            id=t.id,
            name=t.name,
            domain=t.domain,
            description=t.description,
            initial_questions=json.loads(t.initial_questions),
            follow_up_patterns=json.loads(t.follow_up_patterns) if t.follow_up_patterns else None,
            target_style=t.target_style,
            target_tone=t.target_tone,
            voice_persona=t.voice_persona,
            is_active=t.is_active,
            created_by=t.created_by,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in templates
    ]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template by ID."""
    template = await crud.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse(
        id=template.id,
        name=template.name,
        domain=template.domain,
        description=template.description,
        initial_questions=json.loads(template.initial_questions),
        follow_up_patterns=json.loads(template.follow_up_patterns) if template.follow_up_patterns else None,
        target_style=template.target_style,
        target_tone=template.target_tone,
        voice_persona=template.voice_persona,
        is_active=template.is_active,
        created_by=template.created_by,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a template (admin only)."""
    # Prepare update data
    update_data = {}
    if template_update.name is not None:
        update_data["name"] = template_update.name
    if template_update.domain is not None:
        update_data["domain"] = template_update.domain
    if template_update.description is not None:
        update_data["description"] = template_update.description
    if template_update.initial_questions is not None:
        update_data["initial_questions"] = json.dumps(template_update.initial_questions)
    if template_update.follow_up_patterns is not None:
        update_data["follow_up_patterns"] = json.dumps(template_update.follow_up_patterns)
    if template_update.target_style is not None:
        update_data["target_style"] = template_update.target_style
    if template_update.target_tone is not None:
        update_data["target_tone"] = template_update.target_tone
    if template_update.voice_persona is not None:
        update_data["voice_persona"] = template_update.voice_persona
    if template_update.is_active is not None:
        update_data["is_active"] = template_update.is_active
    
    template = await crud.update_template(db, template_id, update_data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse(
        id=template.id,
        name=template.name,
        domain=template.domain,
        description=template.description,
        initial_questions=json.loads(template.initial_questions),
        follow_up_patterns=json.loads(template.follow_up_patterns) if template.follow_up_patterns else None,
        target_style=template.target_style,
        target_tone=template.target_tone,
        voice_persona=template.voice_persona,
        is_active=template.is_active,
        created_by=template.created_by,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a template (soft delete, admin only)."""
    success = await crud.delete_template(db, template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return {"message": "Template deleted successfully"} 