# 🎤 AI Interviewer Platform

An advanced multi-agent AI system that conducts voice-based interviews and automatically generates polished, publishable articles from the conversations. Now with comprehensive authentication, templates, analytics, export options, and real-time transcript display!

## 🚀 Project Status: Phase 5 Complete! ✅

All development phases have been successfully completed:

- ✅ **Phase 1**: Core Agent Logic - Multi-agent workflow with Pydantic AI
- ✅ **Phase 2**: API Backend & Persistence - FastAPI with async SQLite
- ✅ **Phase 3**: Voice Integration - ElevenLabs STT/TTS with WebSocket streaming
- ✅ **Phase 4**: Containerization & Deployment - Docker containerization and cloud deployment scripts
- ✅ **Phase 5**: Production Features - Authentication, Templates, Analytics, Export & Real-time Transcripts

The platform is now enterprise-ready and production-deployed with comprehensive features!

## 🌟 New Features in Phase 5

### 🔐 **Authentication System**

- JWT-based secure authentication with refresh tokens
- User registration, login, and profile management
- Role-based access control (admin/user permissions)
- Protected API endpoints and user-specific data isolation

### 📋 **Interview Templates**

- Pre-designed templates for different domains (journalism, research, marketing, etc.)
- Customizable initial questions and follow-up patterns
- Voice persona and style configuration
- Admin-managed template library with domain categorization

### 📊 **Analytics Dashboard**

- Real-time metrics and performance tracking
- User engagement analytics and retention metrics
- API usage monitoring and cost analysis
- Interactive charts with popular topics and completion rates
- Comprehensive dashboard with export capabilities

### 📤 **Export Options**

- Multi-format export: PDF, DOCX, Markdown, HTML
- Professional document formatting with metadata
- Bulk export functionality for multiple interviews
- Custom styling and branding options

### 🎯 **Real-time Transcript Display**

- Live transcript updates during voice interviews
- Dual-panel interface with controls and transcript
- In-place transcript editing with save functionality
- Search and highlight capabilities across conversations
- Export edited transcripts separately from originals

## 🌟 Core Features

- **Voice-Based Interviews**: Real-time voice conversation using ElevenLabs STT/TTS
- **Multi-Agent Architecture**: Three specialized AI agents working together:
  - **Interviewer Agent**: Conducts dynamic, context-aware interviews
  - **Writer Agent**: Transforms transcripts into well-structured articles
  - **Editor Agent**: Reviews and refines articles through iterative feedback
- **Async API**: High-performance FastAPI backend with WebSocket support
- **Type Safety**: Full Pydantic validation throughout the system
- **Real-time Audio Streaming**: Live audio visualization and processing
- **User Management**: Complete authentication and authorization system
- **Template System**: Flexible interview templates for different use cases
- **Analytics**: Comprehensive usage analytics and performance metrics
- **Export System**: Professional document generation in multiple formats

## 🏗️ Architecture

The platform uses a supervisor-reflection model with three specialized agents:

```
[Voice Input] → [Interviewer Agent] → [Real-time Transcript Display]
                                           ↓
                                    [Writer Agent] ← [Editor Feedback]
                                           ↓              ↑
                                    [Article Draft] → [Editor Agent]
                                           ↓
                                    [Final Article] → [Export System]
                                           ↓
                                    [Analytics Tracking]
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/702ron/ai-interviewer-platform.git
cd ai-interviewer-platform
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure API keys:

```bash
# Copy the .env file and add your API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and ELEVENLABS_API_KEY
```

5. Initialize the database:

```bash
python -c "
import asyncio
from db.database import engine
from db.models import Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Database initialized!')

asyncio.run(init_db())
"
```

6. Run the application:

```bash
python run.py
```

7. Open your browser to http://localhost:8000

## 🎯 Usage

### Getting Started

1. **Register/Login**: Create an account or login at http://localhost:8000
2. **Select Template**: Choose from pre-designed interview templates or create custom interviews
3. **Configure Settings**: Set your interview topic, target audience, and style preferences

### Text-Based Interview

1. Click "Start Text Interview" for a demonstration mode
2. The system generates a mock interview and article
3. Review the generated content and export in your preferred format

### Voice-Based Interview with Real-time Transcripts

1. Click "Start Voice Interview"
2. Allow microphone access when prompted
3. Watch real-time transcript updates in the dual-panel interface
4. Edit transcript content during or after the interview
5. Export your conversation as a professional article

### Analytics & Management

- **Dashboard**: View comprehensive analytics at `/analytics`
- **Templates**: Manage interview templates (admin users)
- **Export History**: Access all your previous interviews and exports
- **User Profile**: Update your account settings and preferences

## 📡 API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile

### Interviews

- `POST /interviews/start` - Start a new interview
- `GET /interviews/{job_id}/status` - Check interview status
- `GET /interviews/{job_id}/result` - Get the generated article
- `WS /interviews/stream/{job_id}` - WebSocket for voice streaming

### Templates

- `GET /templates/` - List available templates
- `POST /templates/` - Create new template (admin)
- `GET /templates/{id}` - Get specific template
- `PUT /templates/{id}` - Update template (admin)

### Analytics

- `GET /analytics/dashboard` - Get dashboard data (admin)
- `GET /analytics/user` - Get user-specific analytics
- `POST /analytics/usage` - Log API usage

### Export

- `GET /interviews/{id}/export/{format}` - Export single interview
- `POST /interviews/batch/export/{format}` - Bulk export

### Transcripts

- `POST /transcripts/save` - Save edited transcript
- `GET /transcripts/interview/{id}` - Get edited transcript
- `GET /transcripts/my` - Get user's edited transcripts

Full API documentation available at http://localhost:8000/docs

## 🛠️ Technology Stack

- **Backend**: FastAPI, Pydantic, SQLAlchemy, JWT Authentication
- **AI Agents**: Pydantic AI, OpenAI GPT-4
- **Voice**: ElevenLabs (STT & TTS)
- **Database**: SQLite (async) with comprehensive analytics models
- **Frontend**: Modern JavaScript with WebRTC and real-time updates
- **Export**: ReportLab (PDF), python-docx (Word), Markdown, HTML
- **Analytics**: Plotly.js for interactive charts and dashboards

## 📁 Project Structure

```
interviewer/
├── api/
│   ├── agents.py              # AI agent definitions
│   ├── interview_handler.py   # Voice interview logic with transcript events
│   ├── auth_routes.py         # Authentication endpoints
│   ├── template_routes.py     # Template management
│   ├── analytics_routes.py    # Analytics and dashboard
│   ├── export_routes.py       # Export functionality
│   └── transcript_routes.py   # Transcript management
├── auth/
│   └── auth_utils.py          # JWT and password utilities
├── db/
│   ├── database.py            # Database configuration
│   ├── models.py              # SQLAlchemy models (users, templates, analytics)
│   └── crud.py                # Database operations
├── static/
│   ├── interview_client_auth.html        # Main authenticated interface
│   ├── interview_voice_transcript.html   # Real-time transcript interface
│   ├── template_admin.html              # Template management
│   └── analytics_dashboard.html         # Analytics dashboard
├── server.py                  # FastAPI application
├── schemas.py                 # Pydantic models
├── voice_service.py           # ElevenLabs integration
└── run.py                     # Startup script
```

## 🔧 Configuration

Environment variables in `.env`:

```env
# AI Model API Keys
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Authentication
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Use Gemini instead of OpenAI
# GOOGLE_API_KEY=your-gemini-api-key
```

## 🧪 Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Lint
flake8 .
```

### Database Management

```bash
# Reset database
rm interviewer.db

# Reinitialize
python -c "
import asyncio
from db.database import engine
from db.models import Base
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init_db())
"
```

## 🔮 Advanced Features

### Custom Templates

Create domain-specific interview templates with:

- Custom initial questions
- Follow-up pattern configurations
- Voice persona settings
- Target style and tone

### Analytics Integration

Track comprehensive metrics including:

- User engagement patterns
- Interview completion rates
- API usage and costs
- Popular topics and templates

### Export Customization

Generate professional documents with:

- Custom branding and styling
- Metadata and timestamps
- Multiple format support
- Bulk processing capabilities

### Real-time Collaboration

- Live transcript editing during interviews
- Save edited versions separately
- Search and highlight functionality
- Export edited transcripts

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Voice powered by [ElevenLabs](https://elevenlabs.io/)
- Authentication using [FastAPI](https://fastapi.tiangolo.com/)
- Analytics with [Plotly.js](https://plotly.com/javascript/)
- Document generation with [ReportLab](https://www.reportlab.com/)
- Inspired by modern AI interviewing and content creation techniques

---

## 🚀 Recent Updates

### Phase 5.5: Real-time Transcript Display ✅

- Live transcript updates during voice interviews
- Professional dual-panel interface
- In-place editing with save functionality
- Search and highlight capabilities
- Separate storage for edited transcripts

### Phase 5.4: Export Options ✅

- PDF, DOCX, Markdown, HTML export formats
- Professional document styling
- Bulk export functionality
- Custom metadata and branding

### Phase 5.3: Analytics Dashboard ✅

- Comprehensive metrics tracking
- Interactive charts and visualizations
- User engagement analytics
- API cost monitoring

### Phase 5.2: Interview Templates ✅

- Domain-specific template library
- Customizable questions and patterns
- Admin template management
- Voice persona configuration

### Phase 5.1: Authentication System ✅

- JWT-based secure authentication
- User registration and management
- Role-based access control
- Protected API endpoints

**The AI Interviewer Platform is now production-ready with enterprise-grade features!** 🎉
