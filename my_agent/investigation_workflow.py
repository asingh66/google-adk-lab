from google.adk.agents import SequentialAgent

from .status_agent import make_status_agent
from .diagnosis_agent import diagnosis_agent


investigation_workflow = SequentialAgent(
    name="investigation_workflow",
    description="Investigates a pipeline by checking its status and then diagnosing it.",
    sub_agents=[
        make_status_agent("investigation_status_agent"),
        diagnosis_agent,
    ],
)
