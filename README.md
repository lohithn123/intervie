# 🎤 AI Interviewer Platform

An advanced multi-agent AI system that conducts voice-based interviews and automatically generates polished, publishable articles from the conversations.

## 🌟 Features

- **Voice-Based Interviews**: Real-time voice conversation using ElevenLabs STT/TTS
- **Multi-Agent Architecture**: Three specialized AI agents working together:
  - **Interviewer Agent**: Conducts dynamic, context-aware interviews
  - **Writer Agent**: Transforms transcripts into well-structured articles
  - **Editor Agent**: Reviews and refines articles through iterative feedback
- **Async API**: High-performance FastAPI backend with WebSocket support
- **Type Safety**: Full Pydantic validation throughout the system
- **Real-time Audio Streaming**: Live audio visualization and processing

## 🏗️ Architecture

The platform uses a supervisor-reflection model with three specialized agents:

```
[Voice Input] → [Interviewer Agent] → [Transcript]
                                           ↓
                                    [Writer Agent] ← [Editor Feedback]
                                           ↓              ↑
                                    [Article Draft] → [Editor Agent]
                                           ↓
                                    [Final Article]
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/interviewer.git
cd interviewer
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

5. Run the application:

```bash
python run.py
```

6. Open your browser to http://localhost:8000

## 🎯 Usage

### Text-Based Interview (Demo Mode)

1. Enter a topic and select target audience
2. Click "Start Text Interview"
3. The system will generate a mock interview and article

### Voice-Based Interview

1. Enter a topic and select target audience
2. Click "Start Voice Interview"
3. Allow microphone access when prompted
4. Have a conversation with the AI interviewer
5. The system will generate an article from your conversation

## 📡 API Endpoints

- `POST /interviews/start` - Start a new interview
- `GET /interviews/{job_id}/status` - Check interview status
- `GET /interviews/{job_id}/result` - Get the generated article
- `WS /interviews/stream/{job_id}` - WebSocket for voice streaming

Full API documentation available at http://localhost:8000/docs

## 🛠️ Technology Stack

- **Backend**: FastAPI, Pydantic, SQLAlchemy
- **AI Agents**: Pydantic AI, OpenAI GPT-4
- **Voice**: ElevenLabs (STT & TTS)
- **Database**: SQLite (async)
- **Frontend**: Vanilla JavaScript with WebRTC

## 📁 Project Structure

```
interviewer/
├── api/
│   ├── agents.py           # AI agent definitions
│   └── interview_handler.py # Voice interview logic
├── db/
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   └── crud.py             # Database operations
├── static/
│   └── interview_client.html # Web interface
├── server.py               # FastAPI application
├── schemas.py              # Pydantic models
├── voice_service.py        # ElevenLabs integration
└── run.py                  # Startup script
```

## 🔧 Configuration

Environment variables in `.env`:

```env
# AI Model API Keys
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

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

## 📈 Future Enhancements

- [ ] Support for multiple languages
- [ ] Custom voice selection
- [ ] Export articles to various formats (PDF, Markdown)
- [ ] Interview templates for different domains
- [ ] Real-time transcript display during voice interviews
- [ ] Integration with content management systems

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Voice powered by [ElevenLabs](https://elevenlabs.io/)
- Inspired by modern AI interviewing techniques
