# Complete OAuth Fix Guide - Google & GitHub Login

## 🔴 Problem

You're experiencing two OAuth errors:

1. **Google OAuth**: "invalid_client The OAuth client was not found" (Error 401)
2. **GitHub OAuth**: "The `redirect_uri` is not associated with this application"

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## ✅ Solution Overview

Both errors occur because:
1. **Redirect URIs are not added** in Google Cloud Console / GitHub OAuth App
2. **Client IDs/Secrets may be missing** in Railway environment variables
3. **Django Site model** may not match your Railway domain

---

## 🔧 Step 1: Fix Google OAuth

### 1.1. Add Redirect URI in Google Cloud Console

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Select your project** (or create a new one)
3. **Navigate to**: **APIs & Services** → **Credentials**
4. **Find your OAuth 2.0 Client ID** (or create a new one):
   - Click **Create Credentials** → **OAuth client ID**
   - Choose **Web application**
   - Name it: "AI Resume Builder Production"
5. **Click Edit** (pencil icon) on your OAuth client
6. **Scroll to "Authorized redirect URIs"**
7. **Click "+ ADD URI"**
8. **Add this EXACT URI**:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
   ⚠️ **CRITICAL**: 
   - Must use `https://` (NOT `http://`)
   - Must end with `/accounts/google/login/callback/`
   - Must include trailing slash `/`
   - Must match your Railway domain exactly
9. **Click SAVE** (very important!)

### 1.2. Verify Railway Environment Variables

**Check if these are set in Railway:**

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Verify these variables exist**:
   - `GOOGLE_OAUTH2_CLIENT_ID` - Should be your Google Client ID
   - `GOOGLE_OAUTH2_CLIENT_SECRET` - Should be your Google Client Secret

**If missing or incorrect:**

1. **Get your Client ID and Secret** from Google Cloud Console:
   - Go to **APIs & Services** → **Credentials**
   - Click on your OAuth client
   - Copy the **Client ID** (starts with numbers like `363779665485-...`)
   - Copy the **Client Secret** (click "Show" if hidden)

2. **Add to Railway**:
   - Go to Railway Dashboard → Your service → Variables
   - Click **+ New Variable**
   - Add `GOOGLE_OAUTH2_CLIENT_ID` with your Client ID
   - Add `GOOGLE_OAUTH2_CLIENT_SECRET` with your Client Secret
   - **Save**

**Using Railway CLI** (alternative):
```bash
railway variables --set "GOOGLE_OAUTH2_CLIENT_ID=your-client-id-here"
railway variables --set "GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret-here"
```

---

## 🔧 Step 2: Fix GitHub OAuth

### 2.1. Add Redirect URI in GitHub OAuth App

1. **Go to [GitHub Developer Settings](https://github.com/settings/developers)**
2. **Click on your OAuth App** (or create a new one):
   - Click **New OAuth App** if you don't have one
   - **Application name**: AI Resume Builder
   - **Homepage URL**: `https://ai-resume-builder-jk.up.railway.app`
   - **Authorization callback URL**: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
3. **Click "Update application"** (or "Register application" if new)
4. **Copy your Client ID** and **generate a Client Secret**:
   - Click on your OAuth App
   - Copy the **Client ID** (visible on the page)
   - Click **Generate a new client secret** (if you don't have one)
   - Copy the **Client Secret** (you won't see it again!)

### 2.2. Verify Railway Environment Variables

**Check if these are set in Railway:**

1. **Go to Railway Dashboard** → Your service → **Variables** tab
2. **Verify these variables exist**:
   - `GITHUB_CLIENT_ID` - Should be your GitHub Client ID
   - `GITHUB_CLIENT_SECRET` - Should be your GitHub Client Secret

**If missing or incorrect:**

1. **Add to Railway**:
   - Go to Railway Dashboard → Your service → Variables
   - Click **+ New Variable**
   - Add `GITHUB_CLIENT_ID` with your GitHub Client ID
   - Add `GITHUB_CLIENT_SECRET` with your GitHub Client Secret
   - **Save**

**Using Railway CLI** (alternative):
```bash
railway variables --set "GITHUB_CLIENT_ID=your-github-client-id"
railway variables --set "GITHUB_CLIENT_SECRET=your-github-client-secret"
```

---

## 🔧 Step 3: Update Django Site Model

The Django Site model **MUST** match your Railway domain. This is critical for OAuth to work!

### Method 1: Using Railway CLI (Recommended)

1. **Open Terminal** and run:
   ```bash
   railway login
   railway link
   railway run python manage.py shell
   ```

2. **In the Python shell, run**:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ai-resume-builder-jk.up.railway.app'
   site.name = 'AI Resume Builder'
   site.save()
   print(f"✅ Site updated: {site.domain}")
   exit()
   ```

### Method 2: Single Command (Alternative)

```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print(f'✅ Site updated: {site.domain}')"
```

### Method 3: Using Django Admin (If accessible)

1. **Go to**: https://ai-resume-builder-jk.up.railway.app/admin/
2. **Login** with your superuser account
3. **Navigate to**: **Sites** → **Sites**
4. **Click on the site** (usually ID=1, "example.com")
5. **Update**:
   - **Domain name**: `ai-resume-builder-jk.up.railway.app`
   - **Display name**: `AI Resume Builder`
6. **Click Save**

---

## 🔧 Step 4: Verify Configuration

### 4.1. Check Railway Variables

**Verify all these variables are set in Railway:**

- ✅ `GOOGLE_OAUTH2_CLIENT_ID`
- ✅ `GOOGLE_OAUTH2_CLIENT_SECRET`
- ✅ `GITHUB_CLIENT_ID`
- ✅ `GITHUB_CLIENT_SECRET`

### 4.2. Check Google Cloud Console

**Verify redirect URI is added:**
- ✅ `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- ✅ Uses `https://` (not `http://`)
- ✅ Has trailing slash `/`
- ✅ Matches Railway domain exactly

### 4.3. Check GitHub OAuth App

**Verify callback URL is set:**
- ✅ `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
- ✅ Uses `https://` (not `http://`)
- ✅ Has trailing slash `/`
- ✅ Matches Railway domain exactly

### 4.4. Check Django Site Model

**Verify Site domain matches:**
- ✅ Domain: `ai-resume-builder-jk.up.railway.app`
- ✅ Name: `AI Resume Builder`

---

## 🧪 Step 5: Test OAuth Login

### 5.1. Wait for Railway Redeploy

After updating environment variables:
- Railway will **automatically redeploy** (wait 1-2 minutes)
- Or manually trigger redeploy in Railway Dashboard

### 5.2. Test Google Login

1. **Go to**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
2. **Click "Sign in with Google"**
3. **Expected**: You should be redirected to Google's consent screen
4. **If error**: Check the steps above

### 5.3. Test GitHub Login

1. **Go to**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
2. **Click "Sign in with GitHub"**
3. **Expected**: You should be redirected to GitHub's authorization page
4. **If error**: Check the steps above

---

## 🔍 Troubleshooting

### Google OAuth Still Not Working?

1. **Check Client ID format**:
   - Should start with numbers like `363779665485-...`
   - Should NOT have `http://` or `https://` prefix
   - Should be the complete Client ID from Google Cloud Console

2. **Verify redirect URI in Google Cloud Console**:
   - Must be: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - Exact match required (including trailing slash)
   - Must use `https://` (not `http://`)

3. **Check Railway logs**:
   ```bash
   railway logs
   ```
   Look for OAuth-related errors

4. **Verify Site model**:
   ```bash
   railway run python manage.py shell
   ```
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   print(f"Site domain: {site.domain}")
   print(f"Site name: {site.name}")
   ```
   Should show: `ai-resume-builder-jk.up.railway.app`

### GitHub OAuth Still Not Working?

1. **Check redirect URI in GitHub OAuth App**:
   - Must be: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
   - Exact match required (including trailing slash)
   - Must use `https://` (not `http://`)

2. **Verify Client ID and Secret in Railway**:
   - Check Railway Dashboard → Variables
   - Make sure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set
   - No extra spaces or quotes

3. **Regenerate Client Secret if needed**:
   - Go to GitHub Developer Settings → Your OAuth App
   - Click "Generate a new client secret"
   - Update Railway with the new secret

4. **Check Railway logs**:
   ```bash
   railway logs
   ```
   Look for OAuth-related errors

### Both Still Not Working?

1. **Verify Site model matches Railway domain**:
   ```bash
   railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1).domain)"
   ```
   Should output: `ai-resume-builder-jk.up.railway.app`

2. **Check Railway environment variables**:
   ```bash
   railway variables
   ```
   Verify all OAuth variables are set

3. **Wait for Railway redeploy**:
   - After changing variables, wait 2-3 minutes
   - Check Railway Dashboard → Deployments
   - Ensure latest deployment is successful

4. **Clear browser cache**:
   - Clear cookies and cache for your Railway domain
   - Try in incognito/private window

---

## 📋 Complete Checklist

### Google OAuth:
- [ ] Redirect URI added in Google Cloud Console: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Client ID set in Railway: `GOOGLE_OAUTH2_CLIENT_ID`
- [ ] Client Secret set in Railway: `GOOGLE_OAUTH2_CLIENT_SECRET`
- [ ] Site model domain matches: `ai-resume-builder-jk.up.railway.app`
- [ ] Railway service redeployed after changes

### GitHub OAuth:
- [ ] Callback URL set in GitHub OAuth App: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
- [ ] Client ID set in Railway: `GITHUB_CLIENT_ID`
- [ ] Client Secret set in Railway: `GITHUB_CLIENT_SECRET`
- [ ] Site model domain matches: `ai-resume-builder-jk.up.railway.app`
- [ ] Railway service redeployed after changes

### Django Site Model:
- [ ] Site domain: `ai-resume-builder-jk.up.railway.app`
- [ ] Site name: `AI Resume Builder`

---

## 🎯 Quick Reference

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

**Google Redirect URI**:
```
https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
```

**GitHub Callback URL**:
```
https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/
```

**Railway Environment Variables**:
- `GOOGLE_OAUTH2_CLIENT_ID`
- `GOOGLE_OAUTH2_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`

**Django Site Model**:
- Domain: `ai-resume-builder-jk.up.railway.app`
- Name: `AI Resume Builder`

---

## 🚀 After Fixing

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Test Google login** - should redirect to Google consent screen
3. **Test GitHub login** - should redirect to GitHub authorization page
4. **Both should work** after completing all steps!

---

**Last Updated**: 2025
**Status**: Complete OAuth Fix Guide for Google & GitHub

