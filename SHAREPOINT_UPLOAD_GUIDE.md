# Upload Dashboard to SharePoint - Get Browser Link

## Method 1: Upload as HTML and Get View Link

### Step 1: Upload to SharePoint
1. Go to your SharePoint site
2. Navigate to a document library (or create one)
3. Click **"Upload"** → **"Files"**
4. Select `dashboard.html` from: `C:\Users\SwanandVaidya\TeamsPsChat\dashboard.html`
5. Click **"Open"**

### Step 2: Get Browser-Viewable Link
1. **Right-click** on the uploaded `dashboard.html` file
2. Click **"Copy link"** or **"Get link"**
3. **IMPORTANT:** Make sure the link permissions are set to **"Anyone with the link can view"** (or your team members)
4. The link will look like:
   ```
   https://yourcompany.sharepoint.com/sites/SiteName/Shared%20Documents/dashboard.html
   ```

### Step 3: Make It Open in Browser (Not Download)
If SharePoint tries to download the file instead of opening it:

**Option A: Rename the file**
- Rename `dashboard.html` to `dashboard.aspx` (SharePoint serves .aspx files in browser)
- Or rename to `index.html` and put it in a folder

**Option B: Use SharePoint Pages**
1. Create a new **SharePoint Page**
2. Add a **"File Viewer"** web part
3. Link it to your `dashboard.html`
4. Publish the page
5. Share the page link (this will open in browser)

**Option C: Direct Link Format**
Modify the SharePoint link to force preview:
```
https://yourcompany.sharepoint.com/sites/SiteName/_layouts/15/WopiFrame.aspx?sourcedoc=/sites/SiteName/Shared%20Documents/dashboard.html&action=default
```

---

## Method 2: Create SharePoint Page (Recommended)

This ensures it opens in browser:

1. Go to your SharePoint site
2. Click **"New"** → **"Page"**
3. Name it: "Survey Dashboard"
4. Click **"Edit"**
5. Click **"+"** to add a web part
6. Choose **"Embed"** or **"File Viewer"**
7. Link to your uploaded `dashboard.html`
8. Click **"Publish"**
9. **Copy the page URL** - this is your shareable link!

**This link will open in browser perfectly!**

---

## Method 3: Upload to SharePoint and Use Direct Link

1. Upload `dashboard.html` to SharePoint
2. Right-click → **"Details"** or **"Properties"**
3. Copy the **"Path"** or **"Server Relative URL"**
4. Your link format:
   ```
   https://yourcompany.sharepoint.com/sites/SiteName/Shared%20Documents/dashboard.html
   ```
5. If it downloads instead of opening, try adding `?web=1` at the end:
   ```
   https://yourcompany.sharepoint.com/sites/SiteName/Shared%20Documents/dashboard.html?web=1
   ```

---

## Quick Test

After getting your link:
1. Paste it in a browser (incognito/private window)
2. It should open the dashboard (not download)
3. If it downloads, use Method 2 (SharePoint Page) instead

---

## Recommended: Method 2 (SharePoint Page)

**Why?**
- ✅ Always opens in browser
- ✅ Looks professional
- ✅ Easy to share
- ✅ Can add to navigation

**Steps:**
1. Upload `dashboard.html` to SharePoint library
2. Create new SharePoint Page
3. Embed the file
4. Publish
5. Share the page link

**This gives you a clean, shareable link that opens in browser!** 🚀

