from google.adk.tools import ToolContext

def get_pipeline_status(
    pipeline_name: str,
    tool_context: ToolContext,
) -> dict:
    """Get the current status of a data pipeline.

    Args:
        pipeline_name: Name of the pipeline to check.

    Returns:
        Information about the current pipeline status.
    """

    # Remember which pipeline the user is working with
    tool_context.state["pipeline_name"] = pipeline_name

    # Simulate a GCP service failure
    if pipeline_name == "broken-pipeline":
        tool_context.state["pipeline_status"] = "UNKNOWN"

        return {
            "pipeline_name": pipeline_name,
            "operation_status": "ERROR",
            "pipeline_status": "UNKNOWN",
            "error": {
                "type": "SERVICE_UNAVAILABLE",
                "message": "Pipeline service is temporarily unavailable",
                "retryable": True,
            },
        }

    pipelines = {
        "customer-orders": {
            "status": "FAILED",
            "last_run": "2026-09-22 14:30:00",
            "error": "BigQuery load job failed",
        },
        "customer-profile": {
            "status": "RUNNING",
            "last_run": "2026-09-22 15:00:00",
            "error": None,
        },
        "daily-sales": {
            "status": "SUCCESS",
            "last_run": "2026-09-22 13:00:00",
            "error": None,
        },
    }

    pipeline = pipelines.get(pipeline_name)

    if pipeline is None:
        tool_context.state["pipeline_status"] = "NOT_FOUND"

        return {
            "pipeline_name": pipeline_name,
            "status": "NOT_FOUND",
        }

    tool_context.state["pipeline_status"] = pipeline["status"]

    return {
        "pipeline_name": pipeline_name,
        **pipeline,
    }


def get_pipeline_logs(pipeline_name: str) -> dict:
    """Get recent logs for a data pipeline.

    Args:
        pipeline_name: Name of the pipeline whose logs should be retrieved.

    Returns:
        Recent log messages for the pipeline.
    """

    logs = {
        "customer-orders": [
            "Starting customer-orders pipeline",
            "Extracted 12,450 records from source",
            "Transform completed successfully",
            "Starting BigQuery load job",
            "ERROR: BigQuery load job failed: destination table not found",
        ],
        "customer-profile": [
            "Starting customer-profile pipeline",
            "Extracted 8,210 customer records",
            "Transform currently running",
        ],
        "daily-sales": [
            "Starting daily-sales pipeline",
            "Extracted 32,100 sales records",
            "Transform completed successfully",
            "BigQuery load completed successfully",
            "Pipeline completed successfully",
        ],
    }

    pipeline_logs = logs.get(pipeline_name)

    if pipeline_logs is None:
        return {
            "pipeline_name": pipeline_name,
            "status": "NOT_FOUND",
            "logs": [],
        }

    return {
        "pipeline_name": pipeline_name,
        "logs": pipeline_logs,
    }


def get_pipeline_metrics(pipeline_name: str) -> dict:
    """Get execution metrics for a data pipeline.

    Args:
        pipeline_name: Name of the pipeline whose metrics should be retrieved.

    Returns:
        Execution metrics for the pipeline.
    """

    metrics = {
        "customer-orders": {
            "records_read": 12450,
            "records_written": 0,
            "records_failed": 12450,
            "duration_seconds": 185,
        },
        "customer-profile": {
            "records_read": 8210,
            "records_written": 0,
            "records_failed": 0,
            "duration_seconds": 92,
        },
        "daily-sales": {
            "records_read": 32100,
            "records_written": 32100,
            "records_failed": 0,
            "duration_seconds": 143,
        },
    }

    pipeline_metrics = metrics.get(pipeline_name)

    if pipeline_metrics is None:
        return {
            "pipeline_name": pipeline_name,
            "status": "NOT_FOUND",
        }

    return {
        "pipeline_name": pipeline_name,
        **pipeline_metrics,
    }


def retry_pipeline(
    pipeline_name: str,
    tool_context: ToolContext,
) -> dict:
    """Retry a failed data pipeline.

    Use this tool only when the user explicitly requests
    that the pipeline be retried.

    Args:
        pipeline_name: Name of the pipeline to retry.

    Returns:
        Result of the retry request.
    """

    valid_pipelines = {
        "customer-orders",
        "customer-profile",
        "daily-sales",
    }

    if pipeline_name not in valid_pipelines:
        return {
            "pipeline_name": pipeline_name,
            "status": "NOT_FOUND",
        }

    retry_approved = tool_context.state.get(
        "retry_approved",
        False,
    )

    if not retry_approved:
        return {
            "pipeline_name": pipeline_name,
            "status": "APPROVAL_REQUIRED",
            "message": (
                f"Retry of {pipeline_name} requires "
                "human approval."
            ),
        }

    return {
        "pipeline_name": pipeline_name,
        "status": "RETRY_STARTED",
        "message": f"Retry started for {pipeline_name}",
    }


def set_test_state(
    tool_context: ToolContext,
) -> dict:
    """Set a test value in the current session state."""

    tool_context.state["test_value"] = "hello-from-day-4"

    return {
        "status": "SUCCESS",
        "message": "Test state was set.",
    }