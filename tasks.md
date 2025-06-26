AI Interviewer Platform: Development Tasks
This document breaks down the project into a concrete, actionable checklist.

Phase 1: Core Agent Logic (Text-Only)

Objective: Create and validate the multi-agent workflow using Pydantic AI. The focus is on the logic, not the interface.

[ ] 1.1: Project Setup

[ ] Initialize a Python project with a virtual environment.
[ ] Install initial dependencies: pydantic-ai[examples], openai, python-dotenv.
[ ] Set up .env file for API keys (OpenAI, ElevenLabs).
[ ] 1.2: Define Core Data Schemas

[ ] Create a schemas.py file.
[ ] Define InterviewMessage(BaseModel) with speaker: str and content: str.
[ ] Define InterviewTranscript(BaseModel) with messages: list[InterviewMessage].
[ ] Define ArticleDraft(BaseModel) with title: str, content: str, version: int.
[ ] Define EditorFeedback(BaseModel) with is_approved: bool, critiques: list[str].
[ ] 1.3: Implement Agents using Pydantic AI

[ ] Create an agents.py file.
[ ] Interviewer Agent:
[ ] Define an InterviewerAgent using pydantic_ai.Agent.
[ ] Give it a system prompt to act as a skilled interviewer.
[ ] Create a (mocked) function that takes a topic and returns a pre-defined InterviewTranscript.
[ ] Writer Agent:
[ ] Define a WriterAgent using pydantic_ai.Agent.
[ ] Set its output_type to the ArticleDraft Pydantic model.
[ ] Give it a system prompt to write an article based on a transcript and target audience.
[ ] Editor Agent:
[ ] Define an EditorAgent using pydantic_ai.Agent.
[ ] Set its output_type to the EditorFeedback Pydantic model.
[ ] Give it a system prompt to critique an article draft and decide if it's publishable.
[ ] 1.4: Orchestrate the Workflow

[ ] Create a main.py file.
[ ] Use Pydantic AI's graph capabilities to define the workflow.
[ ] The graph should flow: Interviewer -> Writer -> Editor.
[ ] Implement a conditional edge after the Editor node:
If is_approved == True, end the workflow.
If is_approved == False, loop back to the Writer node, passing the feedback for the next iteration.
[ ] Write a main function to run the entire process with a sample topic and print the final approved article.
Phase 2: API Backend & Persistence

Objective: Expose the agent workflow via a robust, asynchronous API and persist the results.

[ ] 2.1: Setup FastAPI Application

[ ] Install fastapi, uvicorn[standard], sqlalchemy.
[ ] Create a server.py file and initialize a FastAPI app.
[ ] Structure the project into logical directories (e.g., api, agents, db).
[ ] 2.2: Create Database Models & Logic

[ ] Create a database.py file to handle SQLite connection.
[ ] Create a models.py file using SQLAlchemy to define tables for Interviews and Articles.
[ ] Write CRUD functions to save and retrieve interview transcripts and article drafts.
[ ] 2.3: Develop API Endpoints

[ ] Create an endpoint POST /interviews/start that accepts a topic and target audience.
[ ] This endpoint should immediately return a job_id and trigger the agent workflow in the background.
[ ] Create an endpoint GET /interviews/{job_id}/status to check the progress.
[ ] Create an endpoint GET /interviews/{job_id}/result to fetch the final article.
[ ] 2.4: Integrate Background Tasks

[ ] In the POST /interviews/start endpoint, use BackgroundTasks to run the main agent orchestration function.
[ ] Ensure the background task updates the job status and saves the final result to the SQLite database.
Phase 3: Voice Integration

Objective: Replace the mocked text input with a real-time voice interface.

[ ] 3.1: Integrate ElevenLabs SDK

[ ] Install elevenlabs Python SDK.
[ ] Create a voice_service.py to encapsulate STT and TTS logic.
[ ] 3.2: Implement Real-Time Communication

[ ] Create a WebSocket endpoint in FastAPI: WS /interviews/stream/{job_id}.
[ ] The client will stream microphone audio data to this endpoint.
[ ] The server will stream audio data from the TTS service back to the client.
[ ] 3.3: Connect Voice to Interviewer Agent

[ ] In the WebSocket handler, receive audio chunks from the client.
[ ] Send the audio to the ElevenLabs STT API for transcription.
[ ] Pass the transcribed text to the InterviewerAgent.
[ ] Take the agent's text response and send it to the ElevenLabs TTS API to generate audio.
[ ] Stream the synthesized audio bytes back to the client over the WebSocket.
Phase 4: Front-End & Deployment (High-Level)

Objective: Create a user interface and prepare the application for production.

[ ] 4.1: Build a Simple Front-End

[ ] Use a simple framework like Streamlit or basic HTML/JS.
[ ] Implement client-side JavaScript to access the microphone (using WebRTC) and handle the WebSocket connection.
[ ] Add UI elements to start an interview and display the final article.
[ ] 4.2: Containerize the Application

[ ] Write a Dockerfile for the FastAPI application.
[ ] Use Docker Compose to manage the application and any future services.
[ ] 4.3: Prepare for Deployment

[ ] Configure environment variables for production.
[ ] Write scripts for deploying the container to a cloud service (e.g., AWS, GCP, Azure).
