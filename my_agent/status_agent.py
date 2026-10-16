from google.adk.agents import Agent

from .tools import get_pipeline_status


def make_status_agent(name: str = "status_agent") -> Agent:
    """Build a pipeline status agent.

    An ADK agent instance can only have one parent, and every name must be
    unique within the agent tree, so each parent that needs a status
    specialist builds its own instance under its own name.
    """

    return Agent(
        name=name,
        model="gemini-2.5-flash",
        description="Checks the current status of a data pipeline.",
        instruction="""
You are a pipeline status specialist.

Your responsibility is only to determine the current status of a pipeline.

When asked about a pipeline:
1. Use get_pipeline_status to retrieve its current status.
2. Report the status clearly.
3. Do not diagnose the failure.
4. Do not retrieve logs or metrics.
5. Do not retry the pipeline.

If the pipeline is failed, report that it is failed and leave diagnosis
and remediation to other agents.

If the user did not name a pipeline, do not guess and do not hand the
request back. Ask which pipeline they want checked.
""",
        tools=[get_pipeline_status],
        # Always answer the user directly. Without this the coordinator and
        # this agent can transfer an unanswerable request back and forth
        # forever (seen with "what pipelines are failing?").
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )


status_agent = make_status_agent()
