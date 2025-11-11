# Quick OAuth Fix for Your Railway Domain

## Your Configuration
- **Railway Domain**: `ai-resume-builder-jk.up.railway.app`
- **Project URL**: `https://ai-resume-builder-jk.up.railway.app/`
- **OAuth Callback URL**: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`

## Issues Found
1. ❌ `GOOGLE_OAUTH2_CLIENT_ID` in Railway has `http://` prefix (should be removed)
2. ⚠️ Need to verify redirect URI in Google Cloud Console
3. ⚠️ Need to update Django Site model

## Step-by-Step Fix

### Step 1: Get Your Correct Google Client ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID
4. Copy the **Client ID** (should look like: `363779665485-xxxxx.apps.googleusercontent.com`)
   - ⚠️ **DO NOT** include `http://` or `https://`
   - Just the Client ID itself

### Step 2: Update Railway Environment Variables

**Option A: Via Railway CLI**
```bash
railway variables --set "GOOGLE_OAUTH2_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID_HERE"
```
Replace `YOUR_ACTUAL_CLIENT_ID_HERE` with the Client ID from Step 1 (without `http://`)

**Option B: Via Railway Dashboard**
1. Go to Railway Dashboard → Your Service → Variables
2. Find `GOOGLE_OAUTH2_CLIENT_ID`
3. Edit it and remove the `http://` prefix
4. Save

### Step 3: Update Google Cloud Console Redirect URI

1. In Google Cloud Console → **APIs & Services** → **Credentials**
2. Click **Edit** on your OAuth 2.0 Client ID
3. Under **Authorized redirect URIs**, add:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
4. Click **Save**

### Step 4: Update Django Site Model

Run this command (you'll need to activate your conda environment first):

```bash
conda activate resume_env
railway run python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'ai-resume-builder-jk.up.railway.app'
site.name = 'AI Resume Builder'
site.save()
print(f"✅ Site updated: {site.domain}")
exit()
```

### Step 5: Verify Everything

1. **Check Railway Variables:**
   ```bash
   railway variables | Select-String -Pattern "GOOGLE_OAUTH2"
   ```
   Should show:
   - `GOOGLE_OAUTH2_CLIENT_ID` = Your Client ID (NO `http://`)
   - `GOOGLE_OAUTH2_CLIENT_SECRET` = Your Client Secret

2. **Test Google Sign-In:**
   - Go to: https://ai-resume-builder-jk.up.railway.app/
   - Click "Login" → "Sign in with Google"
   - Should redirect to Google (not show error)

## Common Mistakes to Avoid

❌ **Wrong Client ID format:**
- `http://363779665485-...` ❌
- `https://363779665485-...` ❌
- `363779665485-xxxxx.apps.googleusercontent.com` ✅

❌ **Wrong Redirect URI:**
- `http://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/` ❌ (no `http://`)
- `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback` ❌ (missing trailing `/`)
- `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/` ✅

## Still Not Working?

If you still get "invalid_client" error:
1. Double-check the Client ID in Railway (no `http://` prefix)
2. Verify the redirect URI in Google Cloud Console matches exactly
3. Make sure you saved changes in Google Cloud Console
4. Wait a few minutes for changes to propagate
5. Try again

