# Teams Survey Updates Bot (Python)  Plan

## Goal
Enable a Microsoft Teams chat/bot where a user can subscribe to PureSpectrum live survey updates by providing input (e.g., survey ID). When PureSpectrum sends webhooks, the bot proactively posts updates to the subscribed Teams conversation.

## High-level architecture
- Teams Bot (Python, Bot Framework SDK) running on a web server (FastAPI/Flask/Quart)
- Commands in Teams to manage subscriptions: subscribe <surveyId>, unsubscribe <surveyId>, list, help
- Storage for subscriptions: in-memory to start; optional Redis/SQLite for persistence
- Webhook endpoint to receive PureSpectrum events, validate secret, map to subscribers
- Proactive messaging using conversation references stored at subscribe time
- ngrok (or public hosting) to expose local server for both Teams and PureSpectrum webhooks

## Components
1) Web app server
   - Framework: FastAPI (async, easy routing)
   - Endpoints:
     - POST /api/messages  Bot Framework endpoint for Teams
     - POST /webhooks/purespectrum  incoming events from PureSpectrum
     - GET  /healthz  simple health check

2) Bot adapter and handler
   - Bot Framework SDK for Python (otbuilder-core, otbuilder-schema, otbuilder-integration-aiohttp or otbuilder-integration-fastapi)
   - Capture and store ConversationReference on each message to enable proactive messages
   - Recognize simple text commands with minimal NLP

3) Subscription store
   - Start with in-memory dict: { survey_id: set(conversation_references) }
   - Optional persistence: SQLite via iosqlite or Redis for multi-instance

4) Webhook processing
   - Verify WEBHOOK_SECRET header or signature
   - Validate payload schema (event type, survey id, status/progress fields)
   - Map survey_id to subscribers and send Teams messages

5) Proactive messaging
   - Use dapter.continue_conversation with stored references
   - Format update cards (Adaptive Card optional later; start with text)

## Data flow
- User in Teams:  subscribe 12345
- Bot saves the conversation reference for user/team/channel under survey_id=12345
- PureSpectrum sends webhook: { surveyId: 12345, status: live, completes: 132, ... }
- Webhook handler finds subscribers for 12345 and sends message(s) to those conversations

## Commands
- subscribe <surveyId>  adds current conversation to subscribers of survey
- unsubscribe <surveyId>  removes current conversation from subscribers
- list  shows all surveyIds this conversation is subscribed to
- help  show available commands

## Config (.env)
- MICROSOFT_APP_ID=
- MICROSOFT_APP_PASSWORD=
- WEBHOOK_SECRET=
- PORT=3978
- PUBLIC_BASE_URL=https://<your-ngrok>.ngrok.io

## Implementation steps
1. Create Python venv and 
equirements.txt:
   - otbuilder-core, otbuilder-schema, otbuilder-integration-aiohttp or FastAPI integration
   - astapi, uvicorn, python-dotenv, pydantic
2. Scaffold app structure:
   - pp/main.py (FastAPI app, routes)
   - pp/bot.py (Teams message handling, commands, store refs)
   - pp/adapter.py (BotFrameworkAdapter with credentials)
   - pp/storage.py (SubscriptionStore in-memory; interfaces for persistence)
   - pp/models.py (Webhook payload models)
   - .env, .env.example
3. Implement /api/messages  wire adapter to process activity
4. Implement message commands in ot.py
5. Implement /webhooks/purespectrum with secret validation and payload parsing
6. Implement proactive messaging using stored conversation references
7. Add README.md with setup: create Azure Bot resource, ngrok, set messaging endpoint, add bot to Teams
8. Test locally: send commands in Teams; POST a sample webhook payload and observe bot messages
9. Optional: persistence (SQLite/Redis) and Adaptive Cards

## Sample webhook payload (example)
`
{
  surveyId: 12345,
  event: statusUpdate,
  status: live,
  completes: 132,
  target: 300,
  incidence: 0.21,
  cpi: 2.75,
  updatedAt: 2025-09-19T12:34:56Z
}
`

## Risks / Notes
- Teams proactive messaging requires valid stored conversation references and correct app credentials
- PureSpectrum payload format may differ; confirm actual schema and signing method
- Public HTTPS required for both Teams and PureSpectrum callbacks (use ngrok during dev)
- Consider rate limiting and deduplication if webhooks burst
