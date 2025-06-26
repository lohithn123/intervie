from agents import interviewer_agent, writer_agent, editor_agent, mock_interview
from schemas import InterviewTranscript, ArticleDraft, EditorFeedback
from pydantic_graph import Graph, Node, ConditionalEdge

# Mocked topic and target audience
TOPIC = "Climate Change"
TARGET_AUDIENCE = "General Public"

# Step 1: Get interview transcript (mocked)
transcript = mock_interview(TOPIC)

# Step 2: Define the workflow graph
class State:
    def __init__(self, transcript, draft=None, feedback=None):
        self.transcript = transcript
        self.draft = draft
        self.feedback = feedback

# Nodes
def writer_node(state: State) -> ArticleDraft:
    return writer_agent.run(transcript=state.transcript, target_audience=TARGET_AUDIENCE)

def editor_node(state: State) -> EditorFeedback:
    return editor_agent.run(draft=state.draft)

# Reflection loop
state = State(transcript=transcript)
version = 1
while True:
    # Writer produces a draft
    draft = writer_agent.run(transcript=state.transcript, target_audience=TARGET_AUDIENCE, version=version)
    state.draft = draft
    # Editor reviews the draft
    feedback = editor_agent.run(draft=draft)
    state.feedback = feedback
    print(f"Editor Feedback (v{version}):", feedback.critiques)
    if feedback.is_approved:
        print("\nFinal Approved Article:\n")
        print(f"Title: {draft.title}\n\n{draft.content}")
        break
    version += 1 