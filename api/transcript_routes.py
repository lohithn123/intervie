from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from db.database import AsyncSessionLocal
from db.crud import save_edited_transcript, get_edited_transcript, get_all_edited_transcripts, get_interview
from schemas import EditedTranscriptCreate, EditedTranscriptResponse, TranscriptMessage, UserResponse
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/save", response_model=EditedTranscriptResponse)
async def save_transcript_edits(
    transcript_data: EditedTranscriptCreate,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Save or update an edited transcript for an interview
    
    Users can only edit transcripts for their own interviews
    """
    try:
        # Verify the user owns this interview
        interview = await get_interview(session, transcript_data.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if interview.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied - not your interview")
        
        # Convert Pydantic messages to dict format for JSON storage
        messages_dict = [
            {
                "speaker": msg.speaker,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in transcript_data.messages
        ]
        
        # Save the edited transcript
        saved_transcript = await save_edited_transcript(
            session=session,
            interview_id=transcript_data.interview_id,
            user_id=current_user.id,
            messages=messages_dict,
            edit_notes=transcript_data.edit_notes
        )
        
        # Convert back to response format
        messages_response = [
            TranscriptMessage(
                speaker=msg["speaker"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in json.loads(saved_transcript.messages)
        ]
        
        return EditedTranscriptResponse(
            id=saved_transcript.id,
            interview_id=saved_transcript.interview_id,
            messages=messages_response,
            edit_notes=saved_transcript.edit_notes,
            created_at=saved_transcript.created_at,
            updated_at=saved_transcript.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save transcript: {str(e)}")


@router.get("/interview/{interview_id}", response_model=EditedTranscriptResponse)
async def get_transcript_edits(
    interview_id: int,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get edited transcript for a specific interview
    
    Users can only access transcripts for their own interviews
    """
    try:
        # Verify the user owns this interview
        interview = await get_interview(session, interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if interview.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied - not your interview")
        
        # Get the edited transcript
        transcript = await get_edited_transcript(session, interview_id, current_user.id)
        if not transcript:
            raise HTTPException(status_code=404, detail="No edited transcript found")
        
        # Convert to response format
        messages_response = [
            TranscriptMessage(
                speaker=msg["speaker"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in json.loads(transcript.messages)
        ]
        
        return EditedTranscriptResponse(
            id=transcript.id,
            interview_id=transcript.interview_id,
            messages=messages_response,
            edit_notes=transcript.edit_notes,
            created_at=transcript.created_at,
            updated_at=transcript.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")


@router.get("/my", response_model=List[EditedTranscriptResponse])
async def get_my_edited_transcripts(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get all edited transcripts for the current user
    """
    try:
        transcripts = await get_all_edited_transcripts(
            session=session,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        response_list = []
        for transcript in transcripts:
            messages_response = [
                TranscriptMessage(
                    speaker=msg["speaker"],
                    content=msg["content"],
                    timestamp=msg["timestamp"]
                )
                for msg in json.loads(transcript.messages)
            ]
            
            response_list.append(EditedTranscriptResponse(
                id=transcript.id,
                interview_id=transcript.interview_id,
                messages=messages_response,
                edit_notes=transcript.edit_notes,
                created_at=transcript.created_at,
                updated_at=transcript.updated_at
            ))
        
        return response_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transcripts: {str(e)}")


@router.get("/interview/{interview_id}/export")
async def export_transcript(
    interview_id: int,
    format: str = "txt",  # txt, json
    current_user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Export edited transcript in various formats
    
    Supports: txt (default), json
    """
    try:
        # Verify the user owns this interview
        interview = await get_interview(session, interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if interview.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied - not your interview")
        
        # Get the edited transcript
        transcript = await get_edited_transcript(session, interview_id, current_user.id)
        if not transcript:
            raise HTTPException(status_code=404, detail="No edited transcript found")
        
        messages = json.loads(transcript.messages)
        
        if format.lower() == "json":
            return {
                "interview_id": interview_id,
                "interview_topic": interview.topic,
                "export_date": transcript.updated_at.isoformat(),
                "edit_notes": transcript.edit_notes,
                "messages": messages
            }
        else:  # Default to txt
            from fastapi.responses import PlainTextResponse
            
            # Format as plain text
            text_content = f"Interview Transcript (Edited)\n"
            text_content += f"Topic: {interview.topic}\n"
            text_content += f"Target Audience: {interview.target_audience}\n"
            text_content += f"Last Edited: {transcript.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if transcript.edit_notes:
                text_content += f"Edit Notes: {transcript.edit_notes}\n"
            text_content += f"\n{'='*50}\n\n"
            
            for msg in messages:
                text_content += f"[{msg['timestamp']}] {msg['speaker']}: {msg['content']}\n\n"
            
            return PlainTextResponse(
                content=text_content,
                headers={
                    "Content-Disposition": f"attachment; filename=edited_transcript_{interview_id}.txt"
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export transcript: {str(e)}") 