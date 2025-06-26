"""Real-time interview handler for voice-based conversations."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from schemas import InterviewMessage, InterviewTranscript
from voice_service import transcribe_audio, synthesize_speech, VOICE_PRESETS
from api.agents import interviewer_agent
from pydantic import BaseModel


@dataclass
class ConversationState:
    """Manages the state of an ongoing interview conversation."""
    
    interview_id: int
    topic: str
    messages: List[InterviewMessage] = field(default_factory=list)
    current_audio_buffer: bytes = b""
    is_interviewer_speaking: bool = False
    last_activity: datetime = field(default_factory=datetime.now)
    interview_phase: str = "introduction"  # introduction, main, closing
    questions_asked: int = 0
    
    def add_message(self, speaker: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append(InterviewMessage(speaker=speaker, content=content))
        self.last_activity = datetime.now()
        
    def get_transcript(self) -> InterviewTranscript:
        """Get the current interview transcript."""
        return InterviewTranscript(messages=self.messages)
    
    def get_context_for_agent(self) -> str:
        """Format conversation history for the agent."""
        context = f"Interview topic: {self.topic}\n"
        context += f"Phase: {self.interview_phase}\n"
        context += f"Questions asked so far: {self.questions_asked}\n\n"
        context += "Conversation so far:\n"
        
        for msg in self.messages[-10:]:  # Last 10 messages for context
            context += f"{msg.speaker}: {msg.content}\n"
        
        return context


class InterviewerPromptContext(BaseModel):
    """Context for generating interviewer responses."""
    topic: str
    conversation_context: str
    phase: str
    questions_asked: int


async def handle_interview_audio_stream(
    websocket,
    interview_id: int,
    topic: str,
    target_audience: str
) -> InterviewTranscript:
    """
    Handle real-time audio streaming for an interview session.
    
    Args:
        websocket: FastAPI WebSocket connection
        interview_id: ID of the interview session
        topic: Interview topic
        target_audience: Target audience for the article
        
    Returns:
        Complete interview transcript
    """
    state = ConversationState(interview_id=interview_id, topic=topic)
    silence_threshold = 1.5  # seconds of silence before processing
    
    try:
        # Send initial greeting
        greeting = await generate_interviewer_greeting(topic)
        state.add_message("Interviewer", greeting)
        
        # Synthesize and send greeting audio
        async for audio_chunk in synthesize_speech(
            greeting, 
            voice_id=VOICE_PRESETS["interviewer"]["voice_id"]
        ):
            await websocket.send_bytes(audio_chunk)
        
        # Main interview loop
        while state.questions_asked < 8:  # Limit to 8 questions
            # Receive audio from interviewee
            audio_data = await collect_audio_until_silence(websocket, silence_threshold)
            
            if not audio_data:
                continue
                
            # Transcribe interviewee's response
            transcription = await transcribe_audio(audio_data, diarize=False)
            interviewee_text = transcription.get("text", "").strip()
            
            if not interviewee_text:
                continue
                
            state.add_message("Interviewee", interviewee_text)
            
            # Generate interviewer's next question
            next_question = await generate_next_question(state)
            
            if next_question:
                state.add_message("Interviewer", next_question)
                state.questions_asked += 1
                
                # Update interview phase
                if state.questions_asked >= 6:
                    state.interview_phase = "closing"
                elif state.questions_asked >= 2:
                    state.interview_phase = "main"
                
                # Synthesize and send interviewer's response
                async for audio_chunk in synthesize_speech(
                    next_question,
                    voice_id=VOICE_PRESETS["interviewer"]["voice_id"]
                ):
                    await websocket.send_bytes(audio_chunk)
        
        # Send closing remarks
        closing = await generate_closing_remarks(state)
        state.add_message("Interviewer", closing)
        
        async for audio_chunk in synthesize_speech(
            closing,
            voice_id=VOICE_PRESETS["interviewer"]["voice_id"]
        ):
            await websocket.send_bytes(audio_chunk)
        
        return state.get_transcript()
        
    except Exception as e:
        print(f"Interview error: {str(e)}")
        raise


async def collect_audio_until_silence(
    websocket, 
    silence_threshold: float
) -> bytes:
    """
    Collect audio data until silence is detected.
    
    Args:
        websocket: WebSocket connection
        silence_threshold: Seconds of silence before returning
        
    Returns:
        Collected audio data
    """
    audio_buffer = b""
    silence_start = None
    
    while True:
        try:
            # Set timeout for receiving data
            audio_chunk = await asyncio.wait_for(
                websocket.receive_bytes(), 
                timeout=0.1
            )
            audio_buffer += audio_chunk
            silence_start = None  # Reset silence timer
            
        except asyncio.TimeoutError:
            # No data received, check for silence
            if silence_start is None:
                silence_start = datetime.now()
            elif (datetime.now() - silence_start).total_seconds() > silence_threshold:
                break
    
    return audio_buffer


async def generate_interviewer_greeting(topic: str) -> str:
    """Generate an appropriate greeting for the interview."""
    prompt = f"""
    Generate a warm, professional greeting for an interview about "{topic}".
    The greeting should:
    - Introduce yourself as an AI interviewer
    - Briefly mention the topic
    - Make the interviewee feel comfortable
    - Be concise (2-3 sentences)
    """
    
    result = await interviewer_agent.run(prompt)
    return result.data.messages[0].content


async def generate_next_question(state: ConversationState) -> Optional[str]:
    """Generate the next interview question based on conversation context."""
    context = InterviewerPromptContext(
        topic=state.topic,
        conversation_context=state.get_context_for_agent(),
        phase=state.interview_phase,
        questions_asked=state.questions_asked
    )
    
    prompt = f"""
    Based on the conversation context, generate the next interview question.
    
    Topic: {context.topic}
    Current phase: {context.phase}
    Questions asked: {context.questions_asked}
    
    Recent conversation:
    {context.conversation_context}
    
    Guidelines:
    - Ask follow-up questions based on the interviewee's responses
    - Explore interesting points in more depth
    - Keep questions open-ended and thought-provoking
    - In the closing phase, ask wrap-up questions
    
    Generate only the question, nothing else.
    """
    
    result = await interviewer_agent.run(prompt)
    return result.data.messages[0].content


async def generate_closing_remarks(state: ConversationState) -> str:
    """Generate closing remarks for the interview."""
    prompt = f"""
    Generate brief closing remarks for an interview about "{state.topic}".
    The interview has covered {state.questions_asked} questions.
    
    The closing should:
    - Thank the interviewee for their time and insights
    - Briefly summarize the value of the conversation
    - Be warm and professional
    - Be concise (2-3 sentences)
    """
    
    result = await interviewer_agent.run(prompt)
    return result.data.messages[0].content 