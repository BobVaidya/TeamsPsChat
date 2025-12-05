"""
PureSpectrum Survey Dashboard
Web dashboard for monitoring survey status and quotas
"""
import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, HTMLResponse
from dotenv import load_dotenv

from .web_dashboard import dashboard_home, get_surveys, get_quotas

load_dotenv()

app = FastAPI(title="Survey Dashboard")


@app.get("/healthz")
async def healthz():
	"""Health check endpoint"""
	return PlainTextResponse("ok")


@app.get("/")
async def root():
	"""Redirect root to dashboard"""
	return await dashboard_home()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
	"""Web dashboard for survey monitoring"""
	return await dashboard_home()


@app.get("/api/surveys")
async def api_surveys():
	"""API endpoint to get all live surveys"""
	return await get_surveys()


@app.get("/api/quotas/{survey_id}")
async def api_quotas(survey_id: str):
	"""API endpoint to get quotas for a specific survey"""
	return await get_quotas(survey_id)


if __name__ == "__main__":
	import uvicorn
	port = int(os.getenv("PORT", "8000"))
	uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
