# Rename Repository to SurveyDashboard

## Step 1: Rename on GitHub

1. Go to: https://github.com/BobVaidya/TeamsPsChat/settings
2. Scroll down to "Repository name" section
3. Change from: `TeamsPsChat`
4. To: `SurveyDashboard`
5. Click "Rename" button
6. Confirm the rename

## Step 2: Update Local Git Remote

After renaming on GitHub, run this command locally:

```powershell
git remote set-url origin https://github.com/BobVaidya/SurveyDashboard.git
```

## Step 3: Your New Link

After renaming, your dashboard link will be:
```
https://bobvaidya.github.io/SurveyDashboard/
```

GitHub will automatically redirect the old link to the new one for a while.

## Step 4: Update Any References

If you have the link saved anywhere, update it to:
```
https://bobvaidya.github.io/SurveyDashboard/
```

