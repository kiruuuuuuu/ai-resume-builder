# Google OAuth "invalid_client" Error Fix

## Problem
You're seeing the error: **"invalid_client The OAuth client was not found"** when trying to sign in with Google.

## Root Causes
1. **Client ID not set or incorrect** in Railway environment variables
2. **Redirect URI mismatch** - The redirect URI in Google Cloud Console doesn't match your Railway domain
3. **Site domain not configured** - Django Site model needs to match your Railway domain

## Step-by-Step Fix

### 1. Get Your Railway Domain
Your Railway domain should be something like:
- `ai-resume-builder-jk.up.railway.app` (or similar)

You can find it in:
- Railway Dashboard → Your Service → Settings → Domains
- Or check the URL when you visit your deployed site

### 2. Update Google Cloud Console OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Find your OAuth 2.0 Client ID (or create a new one)
5. Click **Edit** on the OAuth client
6. Under **Authorized redirect URIs**, add:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
   ⚠️ **IMPORTANT**: 
   - Must use `https://` (not `http://`)
   - Must end with `/accounts/google/login/callback/`
   - Replace `ai-resume-builder-jk.up.railway.app` with your actual Railway domain
   - The trailing slash `/` is required

7. Click **Save**

### 3. Verify Railway Environment Variables

Check that these are set correctly in Railway:

```bash
# Using Railway CLI
railway variables
```

Or in Railway Dashboard:
- Go to your service → Variables tab
- Verify these exist:
  - `GOOGLE_OAUTH2_CLIENT_ID` - Should be your Google Client ID (starts with something like `123456789-abc...`)
  - `GOOGLE_OAUTH2_CLIENT_SECRET` - Should be your Google Client Secret

**If they're missing or incorrect:**

```bash
# Set via Railway CLI
railway variables --set "GOOGLE_OAUTH2_CLIENT_ID=your-client-id-here"
railway variables --set "GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret-here"
```

Or in Railway Dashboard:
1. Go to your service → Variables
2. Click **+ New Variable**
3. Add `GOOGLE_OAUTH2_CLIENT_ID` with your Client ID
4. Add `GOOGLE_OAUTH2_CLIENT_SECRET` with your Client Secret

### 4. Update Django Site Model

The Site model in Django must match your Railway domain:

1. **Via Railway CLI:**
   ```bash
   railway run python manage.py shell
   ```
   
   Then in the shell:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ai-resume-builder-jk.up.railway.app'  # Replace with your domain
   site.name = 'AI Resume Builder'
   site.save()
   print(f"Site updated: {site.domain}")
   ```

2. **Via Django Admin (if accessible):**
   - Go to `https://your-railway-domain.com/admin/`
   - Navigate to **Sites** → **Sites**
   - Edit the site (usually ID=1)
   - Set **Domain name** to: `ai-resume-builder-jk.up.railway.app` (your Railway domain)
   - Set **Display name** to: `AI Resume Builder`
   - Save

### 5. Redeploy (if needed)

After updating environment variables or Site model:
- Railway should auto-redeploy when you push changes
- Or manually trigger a redeploy in Railway Dashboard

### 6. Test Again

1. Go to your login page
2. Click "Sign in with Google"
3. You should be redirected to Google's consent screen (not an error page)

## Common Mistakes

❌ **Wrong redirect URI format:**
- `http://...` (should be `https://`)
- Missing trailing slash
- Wrong path (should be `/accounts/google/login/callback/`)

❌ **Client ID/Secret issues:**
- Empty or missing in Railway
- Copied incorrectly (extra spaces, wrong values)
- Using development credentials for production

❌ **Site domain mismatch:**
- Site domain in Django doesn't match Railway domain
- Using `example.com` or `127.0.0.1:8000` in production

## Verification Checklist

- [ ] Google Cloud Console has correct redirect URI with `https://`
- [ ] Railway has `GOOGLE_OAUTH2_CLIENT_ID` set correctly
- [ ] Railway has `GOOGLE_OAUTH2_CLIENT_SECRET` set correctly
- [ ] Django Site model domain matches Railway domain
- [ ] Railway service has been redeployed after changes

## Still Not Working?

1. **Check Railway logs:**
   ```bash
   railway logs
   ```
   Look for any OAuth-related errors

2. **Verify the redirect URI is being constructed correctly:**
   - The redirect URI should be: `https://your-domain/accounts/google/login/callback/`
   - django-allauth constructs this automatically from the Site domain

3. **Double-check Google Cloud Console:**
   - Make sure the OAuth consent screen is configured
   - Verify the OAuth client is enabled (not deleted)
   - Check that you're using the correct project

4. **Test with a fresh OAuth client:**
   - Create a new OAuth client in Google Cloud Console
   - Update Railway with the new Client ID and Secret
   - Make sure redirect URI is added before testing

