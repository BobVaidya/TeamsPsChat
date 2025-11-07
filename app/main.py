from __future__ import annotations

import os
import hmac
import hashlib
import json
from typing import Any, Dict

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv

from botbuilder.core import TurnContext
from botbuilder.schema import Activity

from .adapter import create_adapter
from .bot import SurveyBot
from .models import PureSpectrumEvent, format_event_as_text
from .storage import SubscriptionStore
from .scraper import PureSpectrumScraper


load_dotenv()

app = FastAPI()

adapter = create_adapter()
store = SubscriptionStore()
bot = SurveyBot(store, adapter)


@app.get("/healthz")
async def healthz():
	return PlainTextResponse("ok")


@app.post("/api/messages")
async def messages(request: Request):
	body = await request.json()
	activity = Activity().deserialize(body)
	auth_header = request.headers.get("Authorization", "")

	response: Dict[str, Any] = {}

	async def aux_func(turn_context: TurnContext):
		await bot.on_turn(turn_context)

	await adapter.process_activity(activity, auth_header, aux_func)
	return JSONResponse(response)


def _validate_webhook_secret(request: Request, raw_body: bytes) -> None:
	secret = os.getenv("WEBHOOK_SECRET", "").encode("utf-8")
	if not secret:
		return
	provided = request.headers.get("X-Webhook-Signature") or request.headers.get("X-PureSpectrum-Signature")
	if not provided:
		raise HTTPException(status_code=401, detail="Missing signature header")
	# Simple HMAC SHA256 of raw body; adjust to actual PureSpectrum signing
	computed = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
	if not hmac.compare_digest(computed, provided):
		raise HTTPException(status_code=401, detail="Invalid signature")


@app.post("/webhooks/purespectrum")
async def purespectrum_webhook(request: Request):
	raw = await request.body()
	_validate_webhook_secret(request, raw)
	data = json.loads(raw.decode("utf-8") or "{}")
	event = PureSpectrumEvent.model_validate(data)

	message_text = format_event_as_text(event)
	refs = await store.get_subscribers(event.surveyId)

	for ref in refs:
		async def send_proactive(turn_context: TurnContext):
			await turn_context.send_activity(message_text)

		await adapter.continue_conversation(ref, send_proactive)

	return JSONResponse({"delivered": len(refs)})


# Background task for web scraping
@app.on_event("startup")
async def startup_event():
	"""Start the web scraper in the background"""
	import asyncio
	
	# Get PureSpectrum credentials from environment
	purespectrum_username = os.getenv("PURESPECTRUM_USERNAME")
	purespectrum_password = os.getenv("PURESPECTRUM_PASSWORD")
	
	if purespectrum_username and purespectrum_password:
		scraper = PureSpectrumScraper(purespectrum_username, purespectrum_password)
		
		# Start scraper as background task
		asyncio.create_task(run_scraper_background(scraper, store, adapter))
		print("🔍 Web scraper started - monitoring PureSpectrum dashboard")
	else:
		print("⚠️  PureSpectrum credentials not found. Set PURESPECTRUM_USERNAME and PURESPECTRUM_PASSWORD in .env")

async def run_scraper_background(scraper: PureSpectrumScraper, storage: SubscriptionStore, adapter):
	"""Run the scraper in a background task"""
	import aiohttp
	
	async with aiohttp.ClientSession() as session:
		if await scraper.login(session):
			while True:
				try:
					current_data = await scraper.get_survey_data(session)
					changes = await scraper.detect_changes(current_data)
					
					# Send updates to subscribed conversations
					for change in changes:
						refs = await storage.get_subscribers(change['surveyId'])
						
						for ref in refs:
							async def send_proactive(turn_context):
								await turn_context.send_activity(
									f"🔍 Dashboard Update: Survey {change['surveyId']} - "
									f"{change['status']}, {change['completes']}/{change['target']} completes"
								)
							
							await adapter.continue_conversation(ref, send_proactive)
					
					# Wait before next check (every 2 minutes)
					await asyncio.sleep(120)
					
				except Exception as e:
					print(f"❌ Scraper error: {e}")
					await asyncio.sleep(300)  # Wait 5 minutes on error
		else:
			print("❌ Failed to login to PureSpectrum dashboard")

if __name__ == "__main__":
	import uvicorn

	port = int(os.getenv("PORT", "3978"))
	uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


