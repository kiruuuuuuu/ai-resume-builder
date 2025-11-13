# ✅ Google OAuth Verification Guide

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

**Status from Railway Logs**:
- ✅ Google OAuth Client ID configured: `363779665485-4fdk8ogmaoqvvg2sk...`
- ✅ Google OAuth Client Secret configured
- ✅ Site domain correct: `ai-resume-builder-jk.up.railway.app`

**If you're still getting "invalid_client" error**, the issue is in Google Cloud Console.

---

## 🔍 Step 1: Verify Client ID in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (make sure it's the correct one)
3. **Navigate to**: APIs & Services → Credentials
4. **Find your OAuth 2.0 Client ID** (starts with `363779665485-...`)
5. **Click on it** to view details
6. **Check the Client ID**:
   - Should be: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com` (or similar)
   - Should match Railway variable exactly (character by character)
   - Should end with `.apps.googleusercontent.com`

**If the Client ID doesn't match**:
- Copy the COMPLETE Client ID from Google Cloud Console
- Update Railway variable `GOOGLE_OAUTH2_CLIENT_ID` with the exact value
- Wait 2-3 minutes for Railway to redeploy

---

## 🔍 Step 2: Verify Redirect URI in Google Cloud Console

**This is the most common cause of "invalid_client" errors!**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (the one starting with `363779665485-...`)
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Check if this EXACT URI exists**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```

**If the redirect URI is missing or incorrect**:

1. **Click "+ ADD URI"**
2. **Add this EXACT URI**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
3. **Verify**:
   - ✅ Uses `https://` (NOT `http://`)
   - ✅ Has trailing slash `/`
   - ✅ Matches Railway domain exactly: `ai-resume-builder-jk.up.railway.app`
   - ✅ Path is exactly: `/accounts/google/login/callback/`
4. **Click SAVE** (very important!)

**Common mistakes**:
- ❌ Missing trailing slash: `/accounts/google/login/callback` (should be `/accounts/google/login/callback/`)
- ❌ Using `http://` instead of `https://`
- ❌ Wrong domain: `ai-resume-builder-jk.railway.app` (should be `ai-resume-builder-jk.up.railway.app`)
- ❌ Wrong path: `/account/google/login/callback/` (should be `/accounts/google/login/callback/`)

---

## 🔍 Step 3: Verify OAuth Client Status

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**
4. **Check status**:
   - ✅ Should show "Enabled" (not deleted)
   - ✅ Should be in the correct Google Cloud project
   - ✅ Should be a "Web application" type

**If the OAuth client is deleted or disabled**:
- Create a new OAuth client
- Copy the new Client ID and Secret
- Update Railway variables with new values
- Add the redirect URI before testing

---

## 🔍 Step 4: Verify OAuth Consent Screen

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → OAuth consent screen
3. **Check**:
   - ✅ OAuth consent screen is configured
   - ✅ User type is correct (Internal or External)
   - ✅ App is published (if External)
   - ✅ Test users are added (if in Testing mode)

**If OAuth consent screen is not configured**:
1. **Click "Configure Consent Screen"**
2. **Choose User Type**: Internal (for Google Workspace) or External (for public)
3. **Fill in required fields**:
   - App name: "AI Resume Builder"
   - User support email: Your email
   - Developer contact information: Your email
4. **Click Save and Continue**
5. **Add Scopes** (if needed):
   - `email`
   - `profile`
   - `openid`
6. **Click Save and Continue**
7. **Add Test Users** (if in Testing mode):
   - Add your email address
8. **Click Save and Continue**
9. **Review and Submit**

---

## 🔍 Step 5: Verify Railway Variables

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Check these variables**:
   - `GOOGLE_OAUTH2_CLIENT_ID` - Should be: `363779665485-4fdk8ogmaoqvvg2sk...` (complete)
   - `GOOGLE_OAUTH2_CLIENT_SECRET` - Should be set

**If variables are incorrect**:
1. **Delete the variable**
2. **Get the correct value from Google Cloud Console**
3. **Create a new variable with the exact value**
4. **Save**
5. **Wait 2-3 minutes for Railway to redeploy**

---

## 🔍 Step 6: Test After Changes

1. **Wait 2-3 minutes** after making changes
2. **Clear browser cache** (important!)
3. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
4. **Click "Sign in with Google"**
5. **Expected**: Redirect to Google consent screen (not error page)

---

## 📋 Complete Checklist

### Google Cloud Console:
- [ ] OAuth client exists and is enabled
- [ ] Client ID matches Railway variable exactly: `363779665485-4fdk8ogmaoqvvg2sk...`
- [ ] Redirect URI added: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Redirect URI uses `https://` (not `http://`)
- [ ] Redirect URI has trailing slash `/`
- [ ] Redirect URI matches Railway domain exactly
- [ ] Clicked **SAVE** in Google Cloud Console
- [ ] OAuth consent screen is configured
- [ ] App is published (if External) or test users added (if Testing)

### Railway Variables:
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` is set: `363779665485-4fdk8ogmaoqvvg2sk...`
- [ ] Client ID matches Google Cloud Console exactly
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` is set
- [ ] Client Secret matches Google Cloud Console

### Django Site Model:
- [ ] Site domain: `ai-resume-builder-jk.up.railway.app` (automatic on deployment)

### Testing:
- [ ] Waited 2-3 minutes after making changes
- [ ] Cleared browser cache
- [ ] Tested Google login
- [ ] Should redirect to Google consent screen (not error page)

---

## 🚨 Most Common Issue

**90% of the time**: The redirect URI is not added in Google Cloud Console, or it doesn't match exactly.

**To fix**:
1. Go to Google Cloud Console → Credentials → Your OAuth client → Edit
2. Scroll to "Authorized redirect URIs"
3. Check if this URI exists: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
4. If missing, add it and click SAVE
5. Wait 2-3 minutes and test again

---

## 🔍 Still Not Working?

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

### Check 3: Check OAuth Consent Screen

1. **Google Cloud Console** → OAuth consent screen
2. **Check**: App is published (if External) or test users added (if Testing)
3. **If in Testing mode**: Add your email as a test user

### Check 4: Check Railway Logs

1. **Railway Dashboard** → Your service → Logs
2. **Look for**: OAuth Configuration Check
3. **Verify**: Client ID is configured correctly

---

## 🎯 Quick Fix (If Redirect URI is Missing)

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (starts with `363779665485-...`)
4. **Click Edit** (pencil icon)
5. **Scroll to "Authorized redirect URIs"**
6. **Click "+ ADD URI"**
7. **Add this EXACT URI**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
8. **Click SAVE**
9. **Wait 2-3 minutes**
10. **Test again**

---

**Last Updated**: 2025

