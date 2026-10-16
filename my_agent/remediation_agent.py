from google.adk.agents import Agent

from .tools import retry_pipeline


remediation_agent = Agent(
    name="remediation_agent",
    model="gemini-2.5-flash",
    description="Performs approved remediation actions on a data pipeline.",
    instruction="""
You are a pipeline remediation specialist.

Your responsibility is to perform remediation actions on pipelines.

You may retry a pipeline using retry_pipeline.

Only retry a pipeline when the user has explicitly requested or approved
the retry.

If the user has not explicitly approved the retry, do not call
retry_pipeline. Instead, explain that user approval is required.

Do not diagnose pipeline failures.
Do not retrieve logs or metrics.
""",
    tools=[
        retry_pipeline,
    ],
)