from os import environ

import json

import httpx


# ---------------------------------------------------------
# Google ADK configuration
# ---------------------------------------------------------

ADK_URL = "http://127.0.0.1:8001"
ADK_APP = "my_agent"


def adk_timeout() -> httpx.Timeout:
    """
    Multi-agent investigations can take minutes, so allow a
    long read timeout (override with ADK_TIMEOUT_SECONDS).

    Read per call so values loaded from .env after import apply.
    """

    return httpx.Timeout(
        float(environ.get("ADK_TIMEOUT_SECONDS", "300")),
        connect=10,
    )


# ---------------------------------------------------------
# Google ADK integration
#
# Shared by every channel (Teams / Azure Bot, /chat).
# ---------------------------------------------------------

async def call_adk(
    user_id: str,
    session_id: str,
    message: str,
):
    """
    Sends a user message to the Google ADK application.

    The ADK session is created automatically if it does not
    already exist.
    """

    async with httpx.AsyncClient(timeout=adk_timeout()) as client:

        session_url = (
            f"{ADK_URL}/apps/{ADK_APP}"
            f"/users/{user_id}"
            f"/sessions/{session_id}"
        )

        # Check whether the ADK session already exists.
        session_response = await client.get(session_url)

        if session_response.status_code == 404:

            create_response = await client.post(
                session_url,
                json={},
            )

            create_response.raise_for_status()

        elif session_response.status_code != 200:

            session_response.raise_for_status()

        payload = {
            "appName": ADK_APP,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": message
                    }
                ],
            },
        }

        response = await client.post(
            f"{ADK_URL}/run",
            json=payload,
        )

        response.raise_for_status()

    events = response.json()

    # ADK may return multiple events.
    # Walk backwards through the events and return the
    # latest textual response.
    for event in reversed(events):

        content = event.get("content", {})

        for part in content.get("parts", []):

            text = part.get("text")

            if text and text.strip():
                return text

    return None
