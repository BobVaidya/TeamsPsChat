# Detailed Render Deployment Guide - Step by Step

## Step 1: Create Render Account

1. **Go to Render website:**
   - Open your browser and visit: https://render.com
   
2. **Sign up:**
   - Click the "Get Started for Free" or "Sign Up" button (top right)
   - Choose "Sign up with GitHub" (recommended - easiest)
   - OR sign up with email
   
3. **Authorize GitHub (if using GitHub):**
   - Click "Authorize Render" when prompted
   - This allows Render to access your repositories
   
4. **Complete profile:**
   - Fill in any required information
   - Verify your email if needed

---

## Step 2: Create New Web Service

1. **Go to Dashboard:**
   - After logging in, you'll see the Render dashboard
   - Click the "New +" button (usually in the top right or center)
   
2. **Select Web Service:**
   - From the dropdown menu, select "Web Service"
   - This will start the deployment wizard

---

## Step 3: Connect Your Repository

1. **Connect GitHub:**
   - You'll see options to connect repositories
   - If you used "Sign up with GitHub", your repos should appear
   - If not, click "Configure account" to connect GitHub
   
2. **Select Repository:**
   - Search for: `SurveyDashboard` (or `BobVaidya/SurveyDashboard`)
   - Click on your repository to select it
   - Click "Connect"

---

## Step 4: Configure Web Service Settings

You'll now see a form with several fields. Fill them in as follows:

### Basic Settings:

1. **Name:**
   - Enter: `survey-dashboard-api` (or any name you prefer)
   - This will be part of your URL: `https://survey-dashboard-api.onrender.com`

2. **Region:**
   - Select closest to you (e.g., "Oregon (US West)" or "Frankfurt (EU)")

3. **Branch:**
   - Leave as: `main` (or `master` if that's your default branch)

4. **Root Directory:**
   - Leave empty (unless your app is in a subdirectory)

5. **Runtime:**
   - Select: `Python 3`
   - Render will auto-detect this, but verify it's selected

### Build & Deploy Settings:

6. **Build Command:**
   ```
   pip install -r requirements.txt
   ```
   - This installs all Python dependencies

7. **Start Command:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   - This starts the FastAPI server
   - `$PORT` is automatically set by Render

8. **Plan:**
   - Select: **Free** (for now - you can upgrade later)
   - Free tier includes:
     - 750 hours/month (enough for always-on)
     - May spin down after 15 min inactivity
     - 512 MB RAM

### Advanced Settings (Optional):

9. **Auto-Deploy:**
   - Keep enabled: `Yes`
   - This auto-deploys when you push to GitHub

10. **Health Check Path:**
    - Enter: `/healthz`
    - This helps Render know if your app is running

---

## Step 5: Add Environment Variables

This is CRITICAL - your app needs PureSpectrum credentials:

1. **Scroll down to "Environment Variables" section**

2. **Click "Add Environment Variable"**

3. **Add First Variable:**
   - **Key:** `PURESPECTRUM_USERNAME`
   - **Value:** `svaidya@consultimi.com` (your actual username)
   - Click "Add"

4. **Add Second Variable:**
   - **Key:** `PURESPECTRUM_PASSWORD`
   - **Value:** `your_actual_password` (your PureSpectrum password)
   - Click "Add"
   - ⚠️ **IMPORTANT:** This is sensitive - never share this

5. **Add Third Variable (Optional but recommended):**
   - **Key:** `PORT`
   - **Value:** `10000`
   - Click "Add"
   - (Render sets this automatically, but good to be explicit)

6. **Verify all three variables are listed:**
   - ✅ PURESPECTRUM_USERNAME
   - ✅ PURESPECTRUM_PASSWORD
   - ✅ PORT (optional)

---

## Step 6: Deploy

1. **Review Settings:**
   - Double-check:
     - Build command is correct
     - Start command is correct
     - Environment variables are set
     - Plan is selected (Free)

2. **Click "Create Web Service"**
   - This starts the deployment process

3. **Wait for Deployment:**
   - Render will:
     - Clone your repository
     - Install dependencies (`pip install -r requirements.txt`)
     - Start your application
   - This takes **5-10 minutes** the first time
   - You'll see logs in real-time

---

## Step 7: Monitor Deployment

1. **Watch the Logs:**
   - You'll see build logs scrolling
   - Look for:
     - ✅ "Successfully installed..." messages
     - ✅ "Application is live" message
     - ❌ Any error messages (red text)

2. **Common Issues to Watch For:**
   - **Module not found:** Check `requirements.txt` has all dependencies
   - **Port binding error:** Make sure start command uses `$PORT`
   - **Import errors:** Check your Python code structure

3. **Deployment Status:**
   - Status will show: "Building..." → "Deploying..." → "Live"

---

## Step 8: Verify Deployment

1. **Check Status:**
   - When status shows "Live" (green), your app is running!

2. **Get Your URL:**
   - At the top of the page, you'll see:
     ```
     https://survey-dashboard-api.onrender.com
     ```
   - **COPY THIS URL** - you'll need it for GitHub Pages

3. **Test the API:**
   - Open a new browser tab
   - Visit: `https://your-app-name.onrender.com/healthz`
   - Should see: `ok`
   - If you see "ok", your backend is working! ✅

4. **Test Surveys Endpoint:**
   - Visit: `https://your-app-name.onrender.com/api/surveys`
   - Should see JSON data with surveys (or empty object `{}` if no surveys)
   - If you see JSON, everything is working! ✅

---

## Step 9: Note Your API URL

**IMPORTANT:** Save this URL somewhere:

```
https://your-app-name.onrender.com
```

You'll need this URL in Step 2 when configuring GitHub Pages.

**Example:**
```
https://survey-dashboard-api.onrender.com
```

---

## Troubleshooting

### Issue: "Build failed"
**Solution:**
- Check the build logs for errors
- Common causes:
  - Missing dependencies in `requirements.txt`
  - Syntax errors in Python code
  - Wrong Python version

### Issue: "Application failed to start"
**Solution:**
- Check start command is correct
- Verify `app.main:app` path is correct
- Check environment variables are set

### Issue: "Module not found"
**Solution:**
- Add missing module to `requirements.txt`
- Make sure all dependencies are listed

### Issue: "Failed to authenticate with PureSpectrum"
**Solution:**
- Check environment variables are set correctly
- Verify username/password are correct
- Check `purespectrum_auth.json` token is still valid

### Issue: "Application spins down"
**Solution:**
- Free tier spins down after 15 min inactivity
- First request after spin-down takes 30-60 seconds
- This is normal for free tier
- Upgrade to paid tier ($7/month) for always-on

---

## What Happens Next?

Once your backend is deployed and working:

1. ✅ You have a live API at: `https://your-app.onrender.com`
2. ✅ API endpoints:
   - `/api/surveys` - Get all surveys
   - `/api/quotas/{survey_id}` - Get quotas for a survey
   - `/healthz` - Health check
3. ✅ Ready for Step 2: Configure GitHub Pages

---

## Quick Reference

**Your Render Dashboard:**
- URL: https://dashboard.render.com
- View all services, logs, and settings here

**Your API URL:**
```
https://your-app-name.onrender.com
```

**Test Commands:**
```bash
# Health check
curl https://your-app-name.onrender.com/healthz

# Get surveys
curl https://your-app-name.onrender.com/api/surveys
```

---

## Next Steps

After completing Step 1, proceed to:
- **Step 2:** Enable GitHub Pages and configure the frontend
- See `GITHUB_PAGES_LIVE_SETUP.md` for details

