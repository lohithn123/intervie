from agents import writer_agent, editor_agent, mock_interview
from pydantic_ai._run_context import RunContext
import asyncio

# Mocked topic and target audience
TOPIC = "Climate Change"
TARGET_AUDIENCE = "General Public"

# Step 1: Get interview transcript (mocked)
transcript = mock_interview(RunContext(deps=None, model=None, usage=None, prompt=None), TOPIC)

# Step 2: Define the workflow graph
class State:
    def __init__(self, transcript, draft=None, feedback=None):
        self.transcript = transcript
        self.draft = draft
        self.feedback = feedback

async def main():
    state = State(transcript=transcript)
    version = 1
    while True:
        # Writer produces a draft
        draft_result = await writer_agent.run(transcript=state.transcript, target_audience=TARGET_AUDIENCE, version=version)
        draft = draft_result.output
        state.draft = draft
        # Editor reviews the draft
        feedback_result = await editor_agent.run(draft=draft)
        feedback = feedback_result.output
        state.feedback = feedback
        print(f"Editor Feedback (v{version}):", feedback.critiques)
        if feedback.is_approved:
            print("\nFinal Approved Article:\n")
            print(f"Title: {draft.title}\n\n{draft.content}")
            break
        version += 1

if __name__ == "__main__":
    asyncio.run(main()) 