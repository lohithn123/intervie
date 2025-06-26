AI Interviewer Platform: Development Tasks
This document breaks down the project into a concrete, actionable checklist.

Phase 1: Core Agent Logic (Text-Only)

Objective: Create and validate the multi-agent workflow using Pydantic AI. The focus is on the logic, not the interface.

[x] 1.1: Project Setup

[x] Initialize a Python project with a virtual environment.
[x] Install initial dependencies: pydantic-ai[examples], openai, python-dotenv.
[x] Set up .env file for API keys (OpenAI, ElevenLabs).
[x] 1.2: Define Core Data Schemas

[x] Create a schemas.py file.
[x] Define InterviewMessage(BaseModel) with speaker: str and content: str.
[x] Define InterviewTranscript(BaseModel) with messages: list[InterviewMessage].
[x] Define ArticleDraft(BaseModel) with title: str, content: str, version: int.
[x] Define EditorFeedback(BaseModel) with is_approved: bool, critiques: list[str].
[x] 1.3: Implement Agents using Pydantic AI

[x] Create an agents.py file.
[x] Interviewer Agent:
[x] Define an InterviewerAgent using pydantic_ai.Agent.
[x] Give it a system prompt to act as a skilled interviewer.
[x] Create a (mocked) function that takes a topic and returns a pre-defined InterviewTranscript.
[x] Writer Agent:
[x] Define a WriterAgent using pydantic_ai.Agent.
[x] Set its output_type to the ArticleDraft Pydantic model.
[x] Give it a system prompt to write an article based on a transcript and target audience.
[x] Editor Agent:
[x] Define an EditorAgent using pydantic_ai.Agent.
[x] Set its output_type to the EditorFeedback Pydantic model.
[x] Give it a system prompt to critique an article draft and decide if it's publishable.
[x] 1.4: Orchestrate the Workflow

[x] Create a main.py file.
[x] Use Pydantic AI's graph capabilities to define the workflow.
[x] The graph should flow: Interviewer -> Writer -> Editor.
[x] Implement a conditional edge after the Editor node:
[x] If is_approved == True, end the workflow.
[x] If is_approved == False, loop back to the Writer node, passing the feedback for the next iteration.
[x] Write a main function to run the entire process with a sample topic and print the final approved article.
Phase 2: API Backend & Persistence

Objective: Expose the agent workflow via a robust, asynchronous API and persist the results.

[x] 2.1: Setup FastAPI Application

[x] Install fastapi, uvicorn[standard], sqlalchemy.
[x] Create a server.py file and initialize a FastAPI app.
[x] Structure the project into logical directories (e.g., api, agents, db).
[x] 2.2: Create Database Models & Logic

[x] Create a database.py file to handle SQLite connection.
[x] Create a models.py file using SQLAlchemy to define tables for Interviews and Articles.
[x] Write CRUD functions to save and retrieve interview transcripts and article drafts.
[x] 2.3: Develop API Endpoints

[x] Create an endpoint POST /interviews/start that accepts a topic and target audience.
[x] This endpoint should immediately return a job_id and trigger the agent workflow in the background.
[x] Create an endpoint GET /interviews/{job_id}/status to check the progress.
[x] Create an endpoint GET /interviews/{job_id}/result to fetch the final article.
[x] 2.4: Integrate Background Tasks

[x] In the POST /interviews/start endpoint, use BackgroundTasks to run the main agent orchestration function.
[x] Ensure the background task updates the job status and saves the final result to the SQLite database.
Phase 3: Voice Integration

Objective: Replace the mocked text input with a real-time voice interface.

[x] 3.1: Integrate ElevenLabs SDK

[x] Install elevenlabs Python SDK.
[x] Create a voice_service.py to encapsulate STT and TTS logic.
[x] 3.2: Implement Real-Time Communication

[x] Create a WebSocket endpoint in FastAPI: WS /interviews/stream/{job_id}.
[x] The client will stream microphone audio data to this endpoint.
[x] The server will stream audio data from the TTS service back to the client.
[x] 3.3: Connect Voice to Interviewer Agent

[x] In the WebSocket handler, receive audio chunks from the client.
[x] Send the audio to the ElevenLabs STT API for transcription.
[x] Pass the transcribed text to the InterviewerAgent.
[x] Take the agent's text response and send it to the ElevenLabs TTS API to generate audio.
[x] Stream the synthesized audio bytes back to the client over the WebSocket.
Phase 4: Front-End & Deployment (High-Level)

Objective: Create a user interface and prepare the application for production.

[x] 4.1: Build a Simple Front-End

[x] Use a simple framework like Streamlit or basic HTML/JS.
[x] Implement client-side JavaScript to access the microphone (using WebRTC) and handle the WebSocket connection.
[x] Add UI elements to start an interview and display the final article.
[x] 4.2: Containerize the Application

[x] Write a Dockerfile for the FastAPI application.
[x] Use Docker Compose to manage the application and any future services.
[x] 4.3: Prepare for Deployment

[x] Configure environment variables for production.
[x] Write scripts for deploying the container to a cloud service (e.g., AWS, GCP, Azure).

Phase 5: Optional Enhancements (Future Development)

Objective: Add advanced features to enhance user experience, security, and functionality.

[ ] 5.1: Authentication and User Management

[x] Install authentication dependencies: python-jose[cryptography], passlib[bcrypt], python-multipart.
[x] Create a user model in SQLAlchemy with email, hashed password, and role fields.
[x] Implement JWT token-based authentication with FastAPI security utilities.
[x] Create endpoints for user registration, login, and token refresh.
[x] Add authentication middleware to protect interview endpoints.
[x] Implement user-specific interview history and article ownership.
[ ] Add role-based access control (admin, user, guest).

[ ] 5.2: Interview Templates for Different Domains

[ ] Create a templates model to store predefined interview structures.
[ ] Define template schemas with:
[ ] Domain/category (journalism, research, marketing, etc.)
[ ] Initial questions set
[ ] Follow-up question patterns
[ ] Target article style and tone
[ ] Create an admin interface to manage templates.
[ ] Modify the InterviewerAgent to use templates as context.
[ ] Add template selection to the interview start flow.
[ ] Implement template-specific voice personas.

[ ] 5.3: Analytics Dashboard

[ ] Install dashboard dependencies: plotly, dash or streamlit.
[ ] Create analytics models to track:
[ ] Interview duration and completion rates
[ ] Most common topics
[ ] Article generation success rates
[ ] User engagement metrics
[ ] API usage statistics
[ ] Build dashboard views:
[ ] User activity overview
[ ] Interview performance metrics
[ ] Article quality scores (based on editor iterations)
[ ] Cost analysis (API usage)
[ ] Implement real-time updates using WebSockets.
[ ] Add export functionality for reports.

[ ] 5.4: Export Options (PDF, Markdown, DOCX)

[ ] Install export libraries: reportlab (PDF), python-docx (DOCX), markdown2.
[ ] Create export service module with conversion functions.
[ ] Add export endpoints for each format:
[ ] GET /interviews/{job_id}/export/pdf
[ ] GET /interviews/{job_id}/export/markdown
[ ] GET /interviews/{job_id}/export/docx
[ ] Implement formatting templates for each export type.
[ ] Add metadata to exports (interview date, participants, etc.).
[ ] Create batch export functionality for multiple articles.
[ ] Add email delivery option for exported files.

[ ] 5.5: Real-time Transcript Display

[ ] Modify WebSocket handler to emit transcript events.
[ ] Create transcript state management in interview handler.
[ ] Update frontend to display live transcription:
[ ] Add transcript container to UI
[ ] Implement WebSocket message handling for transcript updates
[ ] Show speaker labels and timestamps
[ ] Add auto-scroll functionality
[ ] Implement transcript editing capabilities:
[ ] Allow users to correct transcription errors
[ ] Add annotation features
[ ] Save edited transcripts separately
[ ] Add transcript search and highlight functionality.
[ ] Create transcript export as separate document.
