# PureSpectrum Survey Dashboard

Web dashboard for monitoring PureSpectrum survey status and quotas.

## Quick Start

The dashboard is live at:
```
https://teamspschat.onrender.com/dashboard
```

## Features

- View all active surveys
- Check survey status with progress bars
- View detailed quota breakdowns
- Real-time data from PureSpectrum

## Local Development

```powershell
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env
PURESPECTRUM_USERNAME=your-email@company.com
PURESPECTRUM_PASSWORD=your-password

# Run locally
python -m app.main
```

Visit: http://localhost:8000/dashboard

## Files

- `app/main.py` - Main FastAPI application
- `app/web_dashboard.py` - Dashboard UI and API endpoints
- `app/scraper.py` - PureSpectrum API integration
- `generate_dashboard.py` - Standalone HTML generator (optional)

## Deployment

Deployed on Render.com - automatically deploys from GitHub.
