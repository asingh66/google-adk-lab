# bot-middleware

FastAPI middleware that connects chat channels to the Google ADK agent (`my_agent`).

```
Teams / Web Chat → Azure Bot → /api/messages → ADK api_server (:8001) → Gemini
```

ADK calls time out after 300s; override with `ADK_TIMEOUT_SECONDS`.
