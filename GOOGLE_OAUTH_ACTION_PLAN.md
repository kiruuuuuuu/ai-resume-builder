# 🚨 Google OAuth Error - Action Plan

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## ⚡ IMMEDIATE ACTION REQUIRED

The error means Google can't find your OAuth client. This **ALWAYS** means one of these:

1. ❌ **Client ID in Railway doesn't match Google Cloud Console exactly**
2. ❌ **Client ID is incomplete/truncated** in Railway
3. ❌ **OAuth client was deleted** in Google Cloud Console
4. ❌ **Redirect URI not added** in Google Cloud Console

---

## 🔧 STEP 1: Check Railway Logs (DO THIS FIRST)

**After Railway redeploys** (2-3 minutes after push), check Railway logs:

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Logs** tab
3. **Look for these messages**:
   - ✅ `✅ Google OAuth Client ID configured: 363779665485-...` (good)
   - ❌ `❌ Google OAuth Client ID format is INCORRECT` (bad - format issue)
   - ⚠️ `⚠️ Google OAuth Client ID NOT SET` (bad - not set)
   - ❌ `Client ID should end with .apps.googleusercontent.com` (bad - incomplete)

**This will tell you exactly what's wrong!**

---

## 🔧 STEP 2: Verify Client ID in Railway

### Check 1: Is Client ID Set?

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Find `GOOGLE_OAUTH2_CLIENT_ID`**
4. **Click on it** to view the full value (Railway might truncate in list view)
5. **Check if it's empty or incomplete**

### Check 2: Does Client ID Match Google Cloud Console?

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (starts with `363779665485-...`)
4. **Click on it** to view details
5. **Copy the COMPLETE Client ID** (should end with `.apps.googleusercontent.com`)
6. **Compare with Railway variable**:
   - Must match EXACTLY (character by character)
   - Must be COMPLETE (not truncated)
   - Must NOT have `http://` or `https://` prefix

### Check 3: Is Client ID Complete?

**Correct format**:
```
363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com
```

**Wrong formats**:
```
❌ 363779665485- (incomplete - missing the rest)
❌ 363779665485 (missing the suffix)
❌ http://363779665485-... (has prefix)
❌ https://363779665485-... (has prefix)
```

---

## 🔧 STEP 3: Fix Client ID in Railway

**If Client ID is wrong or incomplete:**

1. **Get the COMPLETE Client ID from Google Cloud Console**:
   - Go to Google Cloud Console → Credentials
   - Click on your OAuth client
   - Copy the COMPLETE Client ID (should end with `.apps.googleusercontent.com`)

2. **Update Railway**:
   - Go to Railway Dashboard → Variables
   - **Delete `GOOGLE_OAUTH2_CLIENT_ID`** (if exists)
   - **Create new variable**:
     - **Name**: `GOOGLE_OAUTH2_CLIENT_ID`
     - **Value**: Paste the COMPLETE Client ID from Google Cloud Console
     - **Make sure**: No spaces, no prefix, complete value
   - **Save**

3. **Update Client Secret**:
   - **Delete `GOOGLE_OAUTH2_CLIENT_SECRET`** (if exists)
   - **Create new variable**:
     - **Name**: `GOOGLE_OAUTH2_CLIENT_SECRET`
     - **Value**: Paste the Client Secret from Google Cloud Console
   - **Save**

---

## 🔧 STEP 4: Verify Redirect URI in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (the one you're using)
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Check if this EXACT URI exists**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
7. **If missing**:
   - Click "+ ADD URI"
   - Add: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - **Verify**:
     - Uses `https://` (not `http://`)
     - Has trailing slash `/`
     - Matches Railway domain exactly: `ai-resume-builder-jk.up.railway.app`
8. **Click SAVE** (very important!)

---

## 🔧 STEP 5: Verify OAuth Client Status

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Check**:
   - ✅ OAuth client exists (not deleted)
   - ✅ OAuth client is enabled (not disabled)
   - ✅ Using the correct Google Cloud project

**If deleted or disabled:**
- Create a new OAuth client
- Update Railway with new Client ID and Secret
- Add redirect URI before testing

---

## 🔧 STEP 6: Run Diagnostic Command

**After Railway redeploys**, run this command to check OAuth configuration:

```bash
railway run python manage.py check_oauth_config
```

**This will show**:
- ✅ Site model domain
- ✅ Google OAuth Client ID status
- ✅ Google OAuth Client Secret status
- ✅ Expected redirect URIs
- ✅ Any configuration issues

---

## 🔧 STEP 7: Wait and Test

1. **Wait 2-3 minutes** after updating Railway variables
2. **Clear browser cache** (important!)
3. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
4. **Click "Sign in with Google"**
5. **Expected**: Redirect to Google consent screen (not error page)

---

## 🎯 Most Likely Issue (90% of the time)

**The Client ID in Railway doesn't match Google Cloud Console exactly**, or **it's truncated/incomplete**.

**To fix**:
1. Get the COMPLETE Client ID from Google Cloud Console
2. Delete the variable in Railway
3. Create a new one with the complete value
4. Save
5. Wait 2-3 minutes
6. Test again

---

## 📋 Complete Checklist

### Google Cloud Console:
- [ ] OAuth client exists and is enabled
- [ ] Client ID is complete (ends with `.apps.googleusercontent.com`)
- [ ] Redirect URI added: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Redirect URI uses `https://` (not `http://`)
- [ ] Redirect URI has trailing slash `/`
- [ ] Redirect URI matches Railway domain exactly
- [ ] Clicked **SAVE** in Google Cloud Console

### Railway Variables:
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` is set
- [ ] Client ID is COMPLETE (matches Google Cloud Console exactly)
- [ ] Client ID has no `http://` or `https://` prefix
- [ ] Client ID has no extra spaces
- [ ] Client ID ends with `.apps.googleusercontent.com`
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` is set
- [ ] Client Secret matches Google Cloud Console

### Django Site Model:
- [ ] Site domain: `ai-resume-builder-jk.up.railway.app` (automatic on deployment)

### Testing:
- [ ] Checked Railway logs for OAuth configuration messages
- [ ] Waited 2-3 minutes after updating Railway variables
- [ ] Cleared browser cache
- [ ] Tested Google login
- [ ] Should redirect to Google consent screen (not error page)

---

## 🚨 Still Not Working?

### Check Railway Logs

1. **Go to Railway Dashboard** → Your service → **Logs** tab
2. **Look for**:
   - `❌ Google OAuth Client ID format is INCORRECT` → Client ID format is wrong
   - `⚠️ Google OAuth Client ID NOT SET` → Client ID is not set in Railway
   - `Client ID should end with .apps.googleusercontent.com` → Client ID is incomplete

### Run Diagnostic Command

```bash
railway run python manage.py check_oauth_config
```

This will show exactly what's wrong.

### Create New OAuth Client (Last Resort)

If nothing works, create a fresh OAuth client:

1. **Go to Google Cloud Console** → Credentials
2. **Click "Create Credentials"** → OAuth client ID
3. **Choose**: Web application
4. **Name**: "AI Resume Builder Production"
5. **Add redirect URI**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
6. **Click Create**
7. **Copy Client ID and Secret**
8. **Update Railway Variables** with new values
9. **Wait 2-3 minutes** and test

---

## 📚 Documentation

- `GOOGLE_OAUTH_TROUBLESHOOTING.md` - Complete troubleshooting guide
- `docs/GOOGLE_OAUTH_DEBUG.md` - Detailed debugging steps
- `docs/OAUTH_COMPLETE_FIX.md` - Complete OAuth fix guide
- `docs/GOOGLE_OAUTH_FIX.md` - Google OAuth fix guide

---

## 🎯 Quick Reference

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

**Google Redirect URI**:
```
https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
```

**Railway Variables**:
- `GOOGLE_OAUTH2_CLIENT_ID` - Complete Client ID from Google Cloud Console
- `GOOGLE_OAUTH2_CLIENT_SECRET` - Client Secret from Google Cloud Console

**Diagnostic Command**:
```bash
railway run python manage.py check_oauth_config
```

**Check Railway Logs**:
- Go to Railway Dashboard → Your service → Logs
- Look for OAuth configuration messages

---

**Last Updated**: 2025

