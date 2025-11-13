# ⚡ QUICK FIX: Google OAuth "invalid_client" Error

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## 🚨 The Problem

Google can't find your OAuth client. This means one of these:

1. ❌ **Client ID in Railway doesn't match Google Cloud Console exactly** (most common)
2. ❌ **Client ID is incomplete/truncated** in Railway
3. ❌ **Redirect URI not added** in Google Cloud Console
4. ❌ **OAuth client was deleted** in Google Cloud Console

---

## ✅ QUICK FIX (5 minutes)

### Step 1: Get Client ID from Google Cloud Console

1. **Go to**: https://console.cloud.google.com/
2. **Select your project**
3. **Navigate to**: APIs & Services → Credentials
4. **Find your OAuth 2.0 Client ID** (starts with `363779665485-...`)
5. **Click on it** to view details
6. **Copy the COMPLETE Client ID**:
   - Should look like: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
   - Should be COMPLETE (not just `363779665485-`)
   - Should end with `.apps.googleusercontent.com`
7. **Copy the Client Secret**

### Step 2: Update Railway Variables

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Delete `GOOGLE_OAUTH2_CLIENT_ID`** (if exists)
4. **Create new variable**:
   - **Name**: `GOOGLE_OAUTH2_CLIENT_ID`
   - **Value**: Paste the COMPLETE Client ID from Google Cloud Console
   - **Make sure**: No spaces, no prefix, complete value
5. **Delete `GOOGLE_OAUTH2_CLIENT_SECRET`** (if exists)
6. **Create new variable**:
   - **Name**: `GOOGLE_OAUTH2_CLIENT_SECRET`
   - **Value**: Paste the Client Secret from Google Cloud Console
7. **Save**

### Step 3: Add Redirect URI in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Click "+ ADD URI"**
7. **Add this EXACT URI**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
   ⚠️ **CRITICAL**: 
   - Must use `https://` (NOT `http://`)
   - Must have trailing slash `/`
   - Must match Railway domain exactly
8. **Click SAVE** (very important!)

### Step 4: Wait and Test

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Clear browser cache**
3. **Test**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
4. **Click "Sign in with Google"**
5. **Should redirect to Google consent screen** (not error page)

---

## 🔍 Check Railway Logs

**After Railway redeploys**, check Railway logs:

1. **Go to Railway Dashboard** → Your service → **Logs** tab
2. **Look for**:
   - ✅ `✅ Google OAuth Client ID configured: 363779665485-...` (good)
   - ❌ `❌ Google OAuth Client ID format is INCORRECT` (bad - format issue)
   - ⚠️ `⚠️ Google OAuth Client ID NOT SET` (bad - not set)

**This will tell you exactly what's wrong!**

---

## 🎯 Most Common Issue

**90% of the time**: Client ID in Railway doesn't match Google Cloud Console exactly, or it's truncated.

**To fix**:
1. Get the COMPLETE Client ID from Google Cloud Console
2. Delete the variable in Railway
3. Create a new one with the complete value
4. Save
5. Wait 2-3 minutes
6. Test again

---

## 📋 Checklist

- [ ] Client ID in Railway matches Google Cloud Console exactly
- [ ] Client ID is COMPLETE (ends with `.apps.googleusercontent.com`)
- [ ] Redirect URI added in Google Cloud Console: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Clicked **SAVE** in Google Cloud Console
- [ ] Waited 2-3 minutes for Railway redeploy
- [ ] Tested Google login

---

## 📚 Detailed Guides

- `GOOGLE_OAUTH_ACTION_PLAN.md` - Complete action plan
- `docs/GOOGLE_OAUTH_DEBUG.md` - Detailed debugging steps
- `docs/OAUTH_COMPLETE_FIX.md` - Complete OAuth fix guide
- `docs/GOOGLE_OAUTH_FIX.md` - Google OAuth fix guide

---

**Last Updated**: 2025

