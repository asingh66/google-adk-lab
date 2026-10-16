from google.adk.agents import Agent

from .investigation_workflow import investigation_workflow
from .status_agent import status_agent
from .diagnosis_agent import diagnosis_agent
from .remediation_agent import remediation_agent


ccoordinator_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-flash",
    mode="chat",
    description="Coordinates pipeline monitoring, investigation, and remediation.",
    instruction="""
You are the coordinator for pipeline operations.

Delegate work based on the user's intent.

Use status_agent when the user only wants the current status
of a pipeline.

Use investigation_workflow when the user wants to investigate
or diagnose why a pipeline failed.

Use remediation_agent only when the user explicitly requests
or approves a remediation action such as retrying a pipeline.

Do not perform pipeline operations yourself.
""",
    sub_agents=[       
        investigation_workflow,
        remediation_agent,
        1
    ],
)