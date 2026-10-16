from os import environ
import logging

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel

from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    MemoryStorage,
    TurnContext,
    TurnState,
)
from microsoft_agents.hosting.fastapi import (
    CloudAdapter,
    jwt_authorization_decorator,
    start_agent_process,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

# Temporary DEBUG logging while we diagnose the Bot Framework
# authentication / 401 problem.
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("microsoft_agents").setLevel(logging.DEBUG)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI()


# ---------------------------------------------------------
# Google ADK configuration
# ---------------------------------------------------------

ADK_URL = "http://127.0.0.1:8001"
ADK_APP = "my_agent"


# ---------------------------------------------------------
# Microsoft Agents SDK configuration
# ---------------------------------------------------------

agents_sdk_config = load_configuration_from_env(environ)

storage = MemoryStorage()

connection_manager = MsalConnectionManager(
    **agents_sdk_config
)

adapter = CloudAdapter(
    connection_manager=connection_manager
)

authorization = Authorization(
    storage,
    connection_manager,
    **agents_sdk_config
)

agent_app = AgentApplication[TurnState](
    storage=storage,
    adapter=adapter,
    authorization=authorization,
    **agents_sdk_config
)


# The inbound JWT check reads its config from app.state.
# Without this it cannot validate tokens and returns 500.
app.state.agent_configuration = (
    connection_manager.get_default_connection_configuration()
)


# ---------------------------------------------------------
# Request model for local /chat endpoint
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    user_id: str
    message: str


# ---------------------------------------------------------
# Google ADK integration
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

    async with httpx.AsyncClient(timeout=60) as client:

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

        # Send the message to ADK.
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


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "UP"
    }


# ---------------------------------------------------------
# Local test endpoint
#
# This lets us test:
#
# FastAPI -> ADK -> Gemini
#
# without going through Microsoft Bot Framework.
# ---------------------------------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):

    session_id = f"session-{request.user_id}"

    response_text = await call_adk(
        user_id=request.user_id,
        session_id=session_id,
        message=request.message,
    )

    return {
        "response": response_text
    }


# ---------------------------------------------------------
# Microsoft Bot / Teams message handler
#
# Flow:
#
# Teams / Web Chat
#       ↓
# Azure Bot
#       ↓
# /api/messages
#       ↓
# Microsoft Agents SDK
#       ↓
# this handler
#       ↓
# Google ADK
#       ↓
# Gemini
# ---------------------------------------------------------

@agent_app.activity("message")
async def on_message(
    context: TurnContext,
    state: TurnState,
):

    message = context.activity.text

    # Ignore activities that do not contain text.
    if not message:
        return

    # Microsoft user ID becomes the ADK user ID.
    user_id = context.activity.from_property.id

    # Microsoft conversation ID becomes the ADK session ID.
    #
    # This allows ADK conversation memory to follow the
    # Microsoft conversation.
    conversation_id = context.activity.conversation.id

    response_text = await call_adk(
        user_id=user_id,
        session_id=conversation_id,
        message=message,
    )

    if response_text:

        await context.send_activity(
            response_text
        )

    else:

        await context.send_activity(
            "I wasn't able to generate a response."
        )


# ---------------------------------------------------------
# Microsoft Bot Framework endpoint
# ---------------------------------------------------------

@app.post("/api/messages")
@jwt_authorization_decorator
async def messages(request: Request):

    return await start_agent_process(
        request,
        agent_app,
        adapter,
    )