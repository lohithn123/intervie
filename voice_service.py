import os
from elevenlabs import ElevenLabs

# Load API key from environment variable
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Placeholder for async STT function
def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text using ElevenLabs STT."""
    # TODO: Implement real STT call
    pass

# Placeholder for async TTS function
def synthesize_speech(text: str, voice: str = "Rachel") -> bytes:
    """Synthesize speech from text using ElevenLabs TTS."""
    # TODO: Implement real TTS call
    pass 