# 🔴 CRITICAL: Complete These Steps to Fix Google OAuth

You're still getting "invalid_client" error. Here's what needs to be done:

## ✅ Step 1: Verify Client ID in Railway Dashboard

The CLI might show truncated values. **Check in Railway Dashboard:**

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Find `GOOGLE_OAUTH2_CLIENT_ID`
3. **It MUST be the complete value:**
   ```
   363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com
   ```
4. If it's incomplete (showing only `363779665485-`), **edit it** and paste the full Client ID
5. Save

## ✅ Step 2: Add Redirect URI in Google Cloud Console

**THIS IS CRITICAL - Most common cause of the error!**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
4. Click **Edit** (pencil icon)
5. Scroll to **Authorized redirect URIs**
6. Click **+ ADD URI**
7. **Add this EXACT URI:**
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
8. **Click SAVE** (very important!)

## ✅ Step 3: Update Django Site Model

Run this (activate conda first):

```bash
conda activate resume_env
railway run python manage.py shell
```

Then in Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'ai-resume-builder-jk.up.railway.app'
site.name = 'AI Resume Builder'
site.save()
print(f"✅ Site updated: {site.domain}")
exit()
```

## ✅ Step 4: Wait and Test

1. **Wait 2-3 minutes** for Railway to redeploy after variable changes
2. Go to: https://ai-resume-builder-jk.up.railway.app/
3. Click **Login** → **Sign in with Google**
4. Should redirect to Google (not show error)

## 🔍 Troubleshooting

If still not working:

1. **Double-check redirect URI in Google Cloud Console:**
   - Must be: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - Exact match required (including trailing slash)

2. **Verify Client ID in Railway Dashboard:**
   - Should be complete: `363779665485-4fdk8ogmaoqvvg2skvfkn4026seprcim.apps.googleusercontent.com`
   - No `http://` or `https://` prefix

3. **Check Railway logs:**
   ```bash
   railway logs
   ```
   Look for any OAuth-related errors

4. **Verify Site model:**
   - Domain should be: `ai-resume-builder-jk.up.railway.app`
   - Not `example.com` or `127.0.0.1:8000`

## ⚠️ Most Common Issue

**90% of the time, the problem is Step 2** - the redirect URI not being added in Google Cloud Console, or not matching exactly.

Make sure:
- ✅ Redirect URI is added in Google Cloud Console
- ✅ It matches exactly: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- ✅ You clicked **SAVE** in Google Cloud Console

