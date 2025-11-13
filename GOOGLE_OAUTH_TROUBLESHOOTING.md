# 🔴 Google OAuth "invalid_client" Error - Complete Troubleshooting

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## 🚨 Critical Check: Client ID Must Match Exactly

The "invalid_client" error means Google can't find your OAuth client. This **ALWAYS** means one of these:

1. ❌ **Client ID in Railway doesn't match Google Cloud Console** (most common)
2. ❌ **Client ID is incomplete/truncated** in Railway
3. ❌ **OAuth client was deleted** in Google Cloud Console
4. ❌ **Using wrong Google Cloud project**

---

## ✅ Step-by-Step Fix (DO THIS FIRST)

### Step 1: Get the EXACT Client ID from Google Cloud Console

1. **Go to**: https://console.cloud.google.com/
2. **Select your project** (make sure it's the correct one)
3. **Navigate to**: **APIs & Services** → **Credentials**
4. **Find your OAuth 2.0 Client ID** (the one starting with `363779665485-...`)
5. **Click on it** to view details (don't just copy from the list)
6. **Copy the Client ID**:
   - Should look like: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
   - Should be COMPLETE (not truncated)
   - Should NOT have `http://` or `https://` prefix
7. **Copy the Client Secret** (click "Show" if hidden)

### Step 2: Verify Client ID in Railway

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Find `GOOGLE_OAUTH2_CLIENT_ID`**
4. **Click on it** to view the full value (Railway might truncate in the list)
5. **Compare with Google Cloud Console**:
   - Must match EXACTLY (character by character)
   - Must be COMPLETE (not truncated)
   - Must NOT have `http://` or `https://` prefix
   - Must NOT have extra spaces

**If it doesn't match or is incomplete:**

1. **Delete the variable** in Railway
2. **Create a new one**:
   - **Name**: `GOOGLE_OAUTH2_CLIENT_ID`
   - **Value**: Paste the COMPLETE Client ID from Google Cloud Console
   - **Make sure**: No spaces, no prefix, complete value
3. **Save**

### Step 3: Add Redirect URI in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (the one you're using)
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Check if this URI exists**:
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

### Step 4: Verify OAuth Client is Enabled

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Check status**: Should show "Enabled" (not deleted)
5. **If deleted**: Create a new OAuth client
6. **If disabled**: Enable it

### Step 5: Wait and Test

1. **Wait 2-3 minutes** after updating Railway variables
2. **Clear browser cache** (important!)
3. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
4. **Click "Sign in with Google"**
5. **Expected**: Redirect to Google consent screen (not error page)

---

## 🔍 Diagnostic: Run OAuth Check Command

**To diagnose the issue, run this command on Railway**:

```bash
railway run python manage.py check_oauth_config
```

**This will show**:
- ✅ Site model domain
- ✅ Google OAuth Client ID status
- ✅ Google OAuth Client Secret status
- ✅ Expected redirect URIs
- ✅ Any configuration issues

**If you can't run Railway CLI**, use Django Admin:

1. **Go to**: https://ai-resume-builder-jk.up.railway.app/admin/
2. **Login** with your superuser account
3. **Navigate to**: Sites → Sites
4. **Check domain**: Should be `ai-resume-builder-jk.up.railway.app`

---

## 🚨 Most Common Issues

### Issue 1: Client ID is Truncated in Railway

**Symptoms**:
- Railway shows: `363779665485-` (incomplete)
- Should show: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`

**Solution**:
1. **Delete the variable** in Railway
2. **Get the COMPLETE Client ID** from Google Cloud Console
3. **Create a new variable** with the complete value
4. **Save**

### Issue 2: Client ID Doesn't Match Google Cloud Console

**Symptoms**:
- Client ID in Railway doesn't match Google Cloud Console exactly
- Even one character difference will cause this error

**Solution**:
1. **Copy Client ID from Google Cloud Console** (not from Railway)
2. **Delete the variable** in Railway
3. **Create a new one** with the exact value from Google Cloud Console
4. **Save**

### Issue 3: Redirect URI Not Added

**Symptoms**:
- Redirect URI is not in Google Cloud Console
- Or redirect URI doesn't match exactly

**Solution**:
1. **Go to Google Cloud Console** → Credentials → Your OAuth client → Edit
2. **Add redirect URI**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
3. **Verify**:
   - Uses `https://` (not `http://`)
   - Has trailing slash `/`
   - Matches Railway domain exactly
4. **Click SAVE**

### Issue 4: OAuth Client is Deleted

**Symptoms**:
- OAuth client doesn't exist in Google Cloud Console
- Or OAuth client is disabled

**Solution**:
1. **Go to Google Cloud Console** → Credentials
2. **Check if OAuth client exists**
3. **If deleted**: Create a new one
4. **If disabled**: Enable it
5. **Copy the new Client ID and Secret**
6. **Update Railway Variables**

### Issue 5: Wrong Google Cloud Project

**Symptoms**:
- Using Client ID from a different Google Cloud project
- OAuth client exists but doesn't work

**Solution**:
1. **Check current Google Cloud project** (top dropdown)
2. **Make sure you're using the correct project**
3. **Verify Client ID matches** the one in Railway
4. **If different project**: Either switch project or create new OAuth client in the correct project

---

## 🔧 Quick Fix Checklist

### Google Cloud Console:
- [ ] OAuth client exists and is enabled
- [ ] Client ID is complete (not truncated)
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
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` is set
- [ ] Client Secret matches Google Cloud Console

### Testing:
- [ ] Waited 2-3 minutes after updating Railway variables
- [ ] Cleared browser cache
- [ ] Tested Google login
- [ ] Should redirect to Google consent screen (not error page)

---

## 🎯 Exact Steps to Fix (Copy-Paste Ready)

### 1. Get Client ID from Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: APIs & Services → Credentials
4. Find your OAuth 2.0 Client ID (starts with `363779665485-...`)
5. Click on it to view details
6. Copy the COMPLETE Client ID (should end with `.apps.googleusercontent.com`)
7. Copy the Client Secret

### 2. Update Railway Variables

1. Go to: https://railway.app
2. Select your project → Your Django service → Variables
3. **Delete `GOOGLE_OAUTH2_CLIENT_ID`** (if exists)
4. **Create new variable**:
   - Name: `GOOGLE_OAUTH2_CLIENT_ID`
   - Value: [Paste COMPLETE Client ID from Google Cloud Console]
   - Make sure: No spaces, no prefix, complete value
5. **Delete `GOOGLE_OAUTH2_CLIENT_SECRET`** (if exists)
6. **Create new variable**:
   - Name: `GOOGLE_OAUTH2_CLIENT_SECRET`
   - Value: [Paste Client Secret from Google Cloud Console]
7. **Save**

### 3. Add Redirect URI in Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Navigate to: APIs & Services → Credentials
3. Find your OAuth 2.0 Client ID
4. Click Edit (pencil icon)
5. Scroll to "Authorized redirect URIs"
6. Click "+ ADD URI"
7. Add: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
8. **Click SAVE**

### 4. Wait and Test

1. Wait 2-3 minutes for Railway to redeploy
2. Clear browser cache
3. Test: https://ai-resume-builder-jk.up.railway.app/accounts/login/
4. Click "Sign in with Google"
5. Should redirect to Google consent screen

---

## 🔍 Still Not Working?

### Run Diagnostic Command

```bash
railway run python manage.py check_oauth_config
```

This will show exactly what's wrong.

### Check Railway Logs

1. Go to Railway Dashboard → Your service → Logs
2. Look for OAuth-related errors
3. Check if Client ID is being read correctly

### Verify Client ID Format

**Correct format**:
```
363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com
```

**Wrong formats**:
```
❌ 363779665485- (incomplete)
❌ http://363779665485-... (has prefix)
❌ https://363779665485-... (has prefix)
❌ 363779665485-... (missing .apps.googleusercontent.com)
```

### Create New OAuth Client (Last Resort)

If nothing works, create a fresh OAuth client:

1. Go to Google Cloud Console → Credentials
2. Click "Create Credentials" → OAuth client ID
3. Choose: Web application
4. Name: "AI Resume Builder Production"
5. Add redirect URI: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
6. Click Create
7. Copy Client ID and Secret
8. Update Railway Variables with new values
9. Wait 2-3 minutes and test

---

## 📋 Complete Verification

### Google Cloud Console:
- [ ] OAuth client exists: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
- [ ] OAuth client is enabled (not deleted)
- [ ] Redirect URI added: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Clicked SAVE

### Railway Variables:
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` = `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com` (exact match)
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` = [Your Client Secret]

### Django Site Model:
- [ ] Site domain: `ai-resume-builder-jk.up.railway.app` (automatic on deployment)

### Testing:
- [ ] Waited 2-3 minutes
- [ ] Cleared browser cache
- [ ] Tested Google login
- [ ] Should redirect to Google consent screen

---

## 🎯 Most Likely Issue

**90% of the time, the issue is**:
- Client ID in Railway doesn't match Google Cloud Console exactly
- OR Client ID is truncated/incomplete in Railway

**To fix**:
1. Get the COMPLETE Client ID from Google Cloud Console
2. Delete the variable in Railway
3. Create a new one with the complete value
4. Save
5. Wait 2-3 minutes
6. Test again

---

**Last Updated**: 2025

