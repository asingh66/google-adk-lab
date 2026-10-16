from google.adk.agents import Agent

from .tools import get_pipeline_logs, get_pipeline_metrics
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def only_diagnose_failed_pipeline(
    callback_context: CallbackContext,
):
    pipeline_status = callback_context.state.get("pipeline_status")

    if pipeline_status != "FAILED":
        return types.Content(
            role="model",
            parts=[
                types.Part(
                    text=f"Pipeline status is {pipeline_status}. "
                         "Diagnosis is not required."
                )
            ],
        )

    return None


diagnosis_agent = Agent(
    name="diagnosis_agent",
    model="gemini-2.5-flash",
    description="Diagnoses why a data pipeline failed.",
    before_agent_callback=only_diagnose_failed_pipeline,

    instruction="""
    You are a pipeline diagnosis specialist.

    The pipeline currently being investigated is:
    {pipeline_name}

    Its last known status is:
    {pipeline_status}

    Your responsibility is to determine why a pipeline failed.

    When diagnosing a failed pipeline:
    1. Use the pipeline_name from the session state.
    2. Retrieve the pipeline logs using get_pipeline_logs.
    3. Retrieve pipeline metrics using get_pipeline_metrics when useful.
    4. Analyze the available evidence.
    5. Explain the likely root cause clearly.
    6. Recommend appropriate corrective actions.

    Do not retry the pipeline.
    Do not perform remediation actions.
    """,
    tools=[
        get_pipeline_logs,
        get_pipeline_metrics,
    ],
)