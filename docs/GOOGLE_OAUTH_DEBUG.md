# 🔍 Google OAuth Debugging Guide

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## 🚨 Most Common Causes

### 1. Client ID Doesn't Match Google Cloud Console

**Problem**: The Client ID in Railway doesn't match the one in Google Cloud Console.

**Solution**:
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Copy the COMPLETE Client ID** (should look like: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`)
5. **Go to Railway Dashboard** → Your service → Variables
6. **Edit `GOOGLE_OAUTH2_CLIENT_ID`**
7. **Paste the complete Client ID** (make sure it's complete, not truncated)
8. **Save**
9. **Wait 2-3 minutes** for Railway to redeploy

### 2. Client ID is Empty or Incomplete

**Problem**: Railway variable is empty or only shows partial Client ID (like `363779665485-`).

**Solution**:
1. **Check Railway Variables**:
   - Go to Railway Dashboard → Variables
   - Find `GOOGLE_OAUTH2_CLIENT_ID`
   - **Verify it shows the complete value** (not truncated)
2. **If truncated**:
   - Delete the variable
   - Create a new one with the complete Client ID from Google Cloud Console
   - **Save**

### 3. Redirect URI Not Added in Google Cloud Console

**Problem**: Redirect URI is not added or doesn't match exactly.

**Solution**:
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (the one starting with `363779665485-...`)
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Check if this URI exists**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
7. **If missing**:
   - Click "+ ADD URI"
   - Add: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - **Make sure**:
     - Uses `https://` (not `http://`)
     - Has trailing slash `/`
     - Matches Railway domain exactly
8. **Click SAVE** (very important!)

### 4. OAuth Client is Deleted or Disabled

**Problem**: The OAuth client in Google Cloud Console was deleted or disabled.

**Solution**:
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Check if your OAuth client exists**
4. **If deleted**: Create a new one
5. **If disabled**: Enable it
6. **Copy the new Client ID and Secret**
7. **Update Railway Variables**

### 5. Wrong Google Cloud Project

**Problem**: Using Client ID from a different Google Cloud project.

**Solution**:
1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Check current project** (top dropdown)
3. **Make sure you're using the correct project**
4. **Verify Client ID matches** the one in Railway

---

## 🔧 Diagnostic Steps

### Step 1: Run OAuth Configuration Check

**Using Railway CLI**:
```bash
railway run python manage.py check_oauth_config
```

**This will show**:
- ✅ Site model domain
- ✅ Google OAuth Client ID status
- ✅ Google OAuth Client Secret status
- ✅ Expected redirect URIs
- ✅ Configuration issues

### Step 2: Verify Railway Variables

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Check these variables**:
   - `GOOGLE_OAUTH2_CLIENT_ID` - Should be complete (not truncated)
   - `GOOGLE_OAUTH2_CLIENT_SECRET` - Should be set

### Step 3: Verify Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Click on it** to view details
5. **Check**:
   - Client ID matches Railway variable exactly
   - Redirect URI is added: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - OAuth client is enabled (not deleted)

### Step 4: Check Railway Logs

1. **Go to Railway Dashboard** → Your service → **Logs** tab
2. **Look for**:
   - OAuth-related errors
   - Client ID validation errors
   - Site domain issues

---

## 🔍 Common Issues & Solutions

### Issue 1: Client ID is Truncated in Railway

**Symptoms**:
- Railway shows: `363779665485-` (incomplete)
- Should show: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`

**Solution**:
1. **Delete the variable** in Railway
2. **Create a new one** with the complete Client ID
3. **Copy from Google Cloud Console** (not from Railway)
4. **Save**

### Issue 2: Client ID Has Extra Spaces

**Symptoms**:
- Client ID has leading/trailing spaces
- Google rejects it

**Solution**:
1. **Edit the variable** in Railway
2. **Remove all spaces** (leading, trailing, middle)
3. **Save**

### Issue 3: Client ID Has http:// or https:// Prefix

**Symptoms**:
- Client ID shows: `https://363779665485-...`
- Should be: `363779665485-...` (no prefix)

**Solution**:
1. **Edit the variable** in Railway
2. **Remove `http://` or `https://` prefix**
3. **Save**

**Note**: The code now automatically strips these prefixes, but it's better to set it correctly.

### Issue 4: Redirect URI Doesn't Match Exactly

**Symptoms**:
- Redirect URI in Google Cloud Console doesn't match exactly
- Missing trailing slash or wrong protocol

**Solution**:
1. **Check redirect URI in Google Cloud Console**
2. **Must be exactly**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
3. **Update if different**
4. **Click SAVE**

### Issue 5: OAuth Client is from Different Project

**Symptoms**:
- Client ID exists but doesn't work
- Error: "OAuth client was not found"

**Solution**:
1. **Check Google Cloud Console project**
2. **Make sure you're using the correct project**
3. **Verify Client ID matches** the one in Railway
4. **If different project**: Either switch project or create new OAuth client

---

## ✅ Step-by-Step Fix (Complete)

### Step 1: Get Correct Client ID from Google Cloud Console

1. **Go to**: https://console.cloud.google.com/
2. **Select your project** (make sure it's the correct one)
3. **Navigate to**: APIs & Services → Credentials
4. **Find your OAuth 2.0 Client ID** (or create a new one)
5. **Click on it** to view details
6. **Copy the Client ID** (complete value, e.g., `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`)
7. **Copy the Client Secret** (click "Show" if hidden)

### Step 2: Update Railway Variables

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Delete `GOOGLE_OAUTH2_CLIENT_ID`** (if exists)
4. **Create new variable**:
   - **Name**: `GOOGLE_OAUTH2_CLIENT_ID`
   - **Value**: Paste the complete Client ID from Google Cloud Console
   - **Make sure**: No spaces, no `http://` or `https://` prefix
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
     - Matches Railway domain exactly
8. **Click SAVE**

### Step 4: Verify Site Model (Automatic)

The Site model is automatically updated on every deployment. If you need to verify:

1. **Go to Django Admin**: https://ai-resume-builder-jk.up.railway.app/admin/
2. **Login** with your superuser account
3. **Navigate to**: Sites → Sites
4. **Check domain**: Should be `ai-resume-builder-jk.up.railway.app`

### Step 5: Wait and Test

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
3. **Click "Sign in with Google"**
4. **Expected**: Redirect to Google consent screen (not error page)

---

## 🔍 Run Diagnostic Command

**To check OAuth configuration**:

```bash
railway run python manage.py check_oauth_config
```

**This will show**:
- Site model domain
- Google OAuth Client ID status
- Google OAuth Client Secret status
- Expected redirect URIs
- Any configuration issues

---

## 📋 Complete Checklist

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
- [ ] Client ID is complete (matches Google Cloud Console exactly)
- [ ] Client ID has no `http://` or `https://` prefix
- [ ] Client ID has no extra spaces
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` is set
- [ ] Client Secret matches Google Cloud Console

### Django Site Model:
- [ ] Site domain: `ai-resume-builder-jk.up.railway.app`
- [ ] Site name: `AI Resume Builder`
- [ ] (Automatically updated on deployment)

### Testing:
- [ ] Waited 2-3 minutes after updating Railway variables
- [ ] Tested Google login
- [ ] Should redirect to Google consent screen (not error page)

---

## 🚨 Still Not Working?

### Check 1: Verify Client ID Matches Exactly

1. **Google Cloud Console** → Credentials → Your OAuth client
2. **Copy Client ID** (complete value)
3. **Railway Dashboard** → Variables → `GOOGLE_OAUTH2_CLIENT_ID`
4. **Compare**: Must match exactly (character by character)

### Check 2: Verify Redirect URI

1. **Google Cloud Console** → Credentials → Your OAuth client → Edit
2. **Check "Authorized redirect URIs"**
3. **Must contain**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
4. **Verify**: Exact match (including trailing slash)

### Check 3: Run Diagnostic Command

```bash
railway run python manage.py check_oauth_config
```

This will show exactly what's wrong.

### Check 4: Create New OAuth Client (Last Resort)

If nothing works, create a fresh OAuth client:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Click "Create Credentials"** → **OAuth client ID**
4. **Choose**: Web application
5. **Name**: "AI Resume Builder Production"
6. **Add redirect URI**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
7. **Click Create**
8. **Copy Client ID and Secret**
9. **Update Railway Variables** with new values
10. **Wait 2-3 minutes** and test

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

---

**Last Updated**: 2025

