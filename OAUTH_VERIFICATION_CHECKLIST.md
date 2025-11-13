# ✅ OAuth Verification Checklist

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## 🔍 Current Status Check

### ✅ Code Configuration (Verified)
- [x] `users/adapters.py` - Updated to redirect new users to dashboard
- [x] `core/settings.py` - OAuth providers configured correctly
- [x] Environment variables: `GOOGLE_OAUTH2_CLIENT_ID`, `GOOGLE_OAUTH2_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- [x] No linter errors

### ⚠️ Google OAuth Issue (Needs Action)

**Error**: "Error 401: invalid_client - The OAuth client was not found"

**Possible Causes**:
1. ❌ Redirect URI not added in Google Cloud Console
2. ❌ Client ID not set in Railway
3. ❌ Client ID in Railway doesn't match Google Cloud Console
4. ❌ Client ID is incomplete (truncated)
5. ❌ Django Site model doesn't match Railway domain

---

## 🔧 Step-by-Step Verification

### Step 1: Verify Google Cloud Console Configuration

1. **Go to**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID** (starts with `363779665485-...`)
4. **Click Edit** (pencil icon)
5. **Check "Authorized redirect URIs"**:
   - ✅ Should contain: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - ✅ Must use `https://` (not `http://`)
   - ✅ Must have trailing slash `/`
   - ✅ Must match Railway domain exactly

**If missing:**
- Click "+ ADD URI"
- Add: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- Click **SAVE**

6. **Copy your Client ID** (full value, e.g., `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`)
7. **Copy your Client Secret**

### Step 2: Verify Railway Environment Variables

1. **Go to**: https://railway.app
2. **Select your project** → **Your Django service** → **Variables** tab
3. **Check these variables exist**:

   **Google OAuth:**
   - `GOOGLE_OAUTH2_CLIENT_ID` - Should match Google Cloud Console Client ID exactly
   - `GOOGLE_OAUTH2_CLIENT_SECRET` - Should match Google Cloud Console Client Secret

   **GitHub OAuth:**
   - `GITHUB_CLIENT_ID` - Should match GitHub OAuth App Client ID
   - `GITHUB_CLIENT_SECRET` - Should match GitHub OAuth App Client Secret

4. **Verify Client ID format**:
   - ✅ Correct: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
   - ❌ Wrong: `363779665485-` (incomplete)
   - ❌ Wrong: `http://363779665485-...` (has prefix)
   - ❌ Wrong: `363779665485-...` (missing `.apps.googleusercontent.com`)

**If incorrect or missing:**
1. Edit the variable in Railway
2. Paste the complete Client ID from Google Cloud Console
3. Make sure no extra spaces or quotes
4. Click **Save**
5. Wait for Railway to redeploy (2-3 minutes)

### Step 3: Verify Django Site Model

**Run this command**:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); print(f'Domain: {site.domain}'); print(f'Name: {site.name}')"
```

**Expected output**:
```
Domain: ai-resume-builder-jk.up.railway.app
Name: AI Resume Builder
```

**If incorrect:**
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

### Step 4: Test OAuth Login

1. **Wait 2-3 minutes** after updating Railway variables
2. **Go to**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
3. **Click "Sign in with Google"**
4. **Expected**: Redirect to Google consent screen
5. **If error**: Check Steps 1-3 again

---

## 🔍 Common Issues & Solutions

### Issue 1: "invalid_client" Error

**Cause**: Client ID not found or doesn't match

**Solution**:
1. Verify Client ID in Railway matches Google Cloud Console exactly
2. Make sure Client ID is complete (not truncated)
3. Check redirect URI is added in Google Cloud Console
4. Verify Django Site model domain matches Railway domain

### Issue 2: "redirect_uri_mismatch" Error

**Cause**: Redirect URI doesn't match

**Solution**:
1. Add redirect URI in Google Cloud Console: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
2. Make sure it uses `https://` (not `http://`)
3. Make sure it has trailing slash `/`
4. Click **SAVE** in Google Cloud Console

### Issue 3: GitHub Login Works But Google Doesn't

**Cause**: Google OAuth configuration is incorrect

**Solution**:
1. Double-check Google Cloud Console redirect URI
2. Verify `GOOGLE_OAUTH2_CLIENT_ID` in Railway
3. Verify `GOOGLE_OAUTH2_CLIENT_SECRET` in Railway
4. Check Django Site model domain

---

## 📋 Complete Checklist

### Google OAuth:
- [ ] Redirect URI added in Google Cloud Console
- [ ] Redirect URI format: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Clicked **SAVE** in Google Cloud Console
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` set in Railway
- [ ] Client ID is complete (not truncated)
- [ ] Client ID matches Google Cloud Console exactly
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` set in Railway
- [ ] Django Site model domain: `ai-resume-builder-jk.up.railway.app`
- [ ] Waited 2-3 minutes for Railway redeploy
- [ ] Tested Google login

### GitHub OAuth:
- [ ] Callback URL set in GitHub OAuth App
- [ ] Callback URL: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
- [ ] `GITHUB_CLIENT_ID` set in Railway
- [ ] `GITHUB_CLIENT_SECRET` set in Railway
- [ ] Tested GitHub login (should work)

---

## 🎯 Quick Fix Commands

### Update Django Site Model:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

### Check Railway Variables:
```bash
railway variables
```

### Check Django Site Model:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1).domain)"
```

---

**Last Updated**: 2025

