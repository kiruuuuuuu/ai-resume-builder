# 🔴 Google OAuth "invalid_client" Error - Step-by-Step Fix

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## ⚡ Quick Fix (5 minutes)

### Step 1: Verify Redirect URI in Google Cloud Console

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Select your project** (the one with your OAuth client)
3. **Navigate to**: **APIs & Services** → **Credentials**
4. **Find your OAuth 2.0 Client ID** (the one starting with `363779665485-...`)
5. **Click Edit** (pencil icon)
6. **Scroll to "Authorized redirect URIs"**
7. **Make sure this EXACT URI is added**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
   ⚠️ **CRITICAL CHECKLIST**:
   - ✅ Must use `https://` (NOT `http://`)
   - ✅ Must end with `/accounts/google/login/callback/`
   - ✅ Must include trailing slash `/`
   - ✅ Must match your Railway domain exactly: `ai-resume-builder-jk.up.railway.app`
8. **If missing, click "+ ADD URI" and add it**
9. **Click SAVE** (very important!)

### Step 2: Verify Client ID in Railway

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Find `GOOGLE_OAUTH2_CLIENT_ID`**
4. **Verify it matches** your Google Cloud Console Client ID:
   - Should start with: `363779665485-...`
   - Should be the COMPLETE Client ID
   - Should NOT have `http://` or `https://` prefix
   - Should NOT have extra spaces

**If incorrect or missing:**
1. **Get Client ID from Google Cloud Console**:
   - Go to **APIs & Services** → **Credentials**
   - Click on your OAuth client
   - Copy the **Client ID** (full value)
2. **Update in Railway**:
   - Go to Railway Dashboard → Variables
   - Edit `GOOGLE_OAUTH2_CLIENT_ID`
   - Paste the complete Client ID
   - **Save**

### Step 3: Verify Client Secret in Railway

1. **In Railway Dashboard** → Variables tab
2. **Find `GOOGLE_OAUTH2_CLIENT_SECRET`**
3. **If missing or incorrect**:
   - Get it from Google Cloud Console → Your OAuth client
   - Click "Show" if hidden
   - Copy the Client Secret
   - Add/Update in Railway Variables
   - **Save**

### Step 4: Update Django Site Model

**Run this command** (if not already done):

```bash
railway login
railway link
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

### Step 5: Wait and Test

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
3. **Click "Sign in with Google"**
4. **Should redirect to Google consent screen** (not error page)

---

## 🔍 Troubleshooting

### Still Getting "invalid_client" Error?

**Check 1: Client ID Format**
- ❌ Wrong: `http://363779665485-...` or `https://363779665485-...`
- ❌ Wrong: `363779665485-` (incomplete)
- ✅ Correct: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com` (complete)

**Check 2: Redirect URI in Google Cloud Console**
- ❌ Wrong: `http://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- ❌ Wrong: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback` (missing trailing slash)
- ✅ Correct: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`

**Check 3: OAuth Client Status**
- Go to Google Cloud Console → Credentials
- Make sure your OAuth client is **Enabled** (not deleted)
- Make sure you're using the **correct project**

**Check 4: Railway Variables**
- Verify `GOOGLE_OAUTH2_CLIENT_ID` is set
- Verify `GOOGLE_OAUTH2_CLIENT_SECRET` is set
- Make sure no extra spaces or quotes

**Check 5: Django Site Model**
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1).domain)"
```
Should output: `ai-resume-builder-jk.up.railway.app`

---

## 📋 Complete Checklist

- [ ] Redirect URI added in Google Cloud Console: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Clicked **SAVE** in Google Cloud Console
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` set in Railway (complete value, no prefix)
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` set in Railway
- [ ] Django Site model domain: `ai-resume-builder-jk.up.railway.app`
- [ ] Waited 2-3 minutes for Railway redeploy
- [ ] Tested Google login

---

## 🎯 Most Common Issues

1. **Redirect URI not added** → Add it in Google Cloud Console and **SAVE**
2. **Client ID incomplete** → Make sure Railway has the complete Client ID
3. **Wrong redirect URI format** → Must be `https://` with trailing slash `/`
4. **Site model mismatch** → Update Django Site model to match Railway domain

---

**Last Updated**: 2025

