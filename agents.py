from pydantic_ai import Agent
from schemas import InterviewTranscript, ArticleDraft, EditorFeedback
from pydantic import BaseModel

# Interviewer Agent (mocked for now)
class InterviewerInput(BaseModel):
    topic: str

class InterviewerOutput(InterviewTranscript):
    pass

interviewer_agent = Agent(
    name="InterviewerAgent",
    system_prompt="You are a skilled interviewer. Your job is to conduct an in-depth interview on a given topic and return a structured transcript. Each message must have a speaker label.",
    input_type=InterviewerInput,
    output_type=InterviewerOutput,
)

@interviewer_agent.tool
def mock_interview(topic: str) -> InterviewTranscript:
    # This is a mocked function for demonstration
    return InterviewTranscript(messages=[
        {"speaker": "Interviewer", "content": f"Let's talk about {topic}. Why is it important?"},
        {"speaker": "Interviewee", "content": "It's important because it impacts many lives."},
        {"speaker": "Interviewer", "content": "What are the biggest challenges?"},
        {"speaker": "Interviewee", "content": "The biggest challenges are awareness and resources."},
    ])

# Writer Agent
def writer_system_prompt():
    return (
        "You are a professional writer. Given an interview transcript and a target audience, write a clear, engaging article draft. "
        "Your output must be structured as an ArticleDraft Pydantic model."
    )

writer_agent = Agent(
    name="WriterAgent",
    system_prompt=writer_system_prompt(),
    output_type=ArticleDraft,
)

# Editor Agent
def editor_system_prompt():
    return (
        "You are a critical editor. Review the article draft for clarity, tone, and factual consistency. "
        "Provide actionable critiques and set is_approved to True only if the article is ready for publication. "
        "Your output must be structured as an EditorFeedback Pydantic model."
    )

editor_agent = Agent(
    name="EditorAgent",
    system_prompt=editor_system_prompt(),
    output_type=EditorFeedback,
) 