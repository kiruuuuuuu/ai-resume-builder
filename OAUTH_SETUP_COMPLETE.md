# Google OAuth Setup - Final Steps

## ✅ What's Been Done

1. ✅ **OAuth Client Created** in Google Cloud Console
2. ✅ **Client ID Set** in Railway (check Railway variables to verify)
3. ✅ **Client Secret Set** in Railway (check Railway variables to verify)

## 🔧 Remaining Steps

### Step 1: Add Redirect URI in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID (the one you just created)
4. Click **Edit** (pencil icon)
5. Under **Authorized redirect URIs**, click **+ ADD URI**
6. Add this exact URI:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
7. Click **Save**

### Step 2: Update Django Site Model

Run this command to update the Site domain:

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

### Step 3: Test Google Sign-In

1. Go to: https://ai-resume-builder-jk.up.railway.app/
2. Click **Login**
3. Click **Sign in with Google**
4. You should be redirected to Google's consent screen (not an error page)

## ⚠️ Important Notes

1. **OAuth Consent Screen**: The dialog mentioned "OAuth access is restricted to the test users listed on your OAuth consent screen". This means:
   - If you're in testing mode, only users added as test users can sign in
   - To allow anyone to sign in, you'll need to publish your OAuth app (requires verification)

2. **Redirect URI**: Must match exactly:
   - ✅ `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - ❌ `http://...` (wrong protocol)
   - ❌ Missing trailing slash
   - ❌ Different domain

3. **Railway Redeploy**: After updating environment variables, Railway should auto-redeploy. Wait a minute or two before testing.

## 🎉 You're Almost Done!

Once you complete Step 1 (adding the redirect URI in Google Cloud Console) and Step 2 (updating the Site model), Google sign-in should work!

