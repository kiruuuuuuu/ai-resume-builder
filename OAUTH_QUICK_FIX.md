# 🚀 OAuth Quick Fix - Step-by-Step

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## ⚡ Quick Steps (5 minutes)

### Step 1: Fix Google OAuth (2 minutes)

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
   - **APIs & Services** → **Credentials**
   - Click **Edit** on your OAuth client
   - Under **Authorized redirect URIs**, click **+ ADD URI**
   - Add: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
   - **Click SAVE**

2. **Verify Railway Variables**:
   - Go to Railway Dashboard → Your service → Variables
   - Check: `GOOGLE_OAUTH2_CLIENT_ID` and `GOOGLE_OAUTH2_CLIENT_SECRET` exist
   - If missing, add them with values from Google Cloud Console

### Step 2: Fix GitHub OAuth (2 minutes)

1. **Go to [GitHub Developer Settings](https://github.com/settings/developers)**
   - Click on your OAuth App (or create new one)
   - Set **Authorization callback URL**: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
   - **Click "Update application"**
   - Copy **Client ID** and **Client Secret**

2. **Verify Railway Variables**:
   - Go to Railway Dashboard → Your service → Variables
   - Check: `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` exist
   - If missing, add them with values from GitHub

### Step 3: Update Django Site Model (1 minute)

**Run this command in Terminal:**

```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

**Or if you're already logged into Railway:**

```bash
railway link
railway run python manage.py shell
```

Then in Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'ai-resume-builder-jk.up.railway.app'
site.name = 'AI Resume Builder'
site.save()
print('✅ Site updated!')
exit()
```

### Step 4: Wait and Test

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Test Google login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/
3. **Test GitHub login**: https://ai-resume-builder-jk.up.railway.app/accounts/login/

---

## 📋 Checklist

### Google OAuth:
- [ ] Redirect URI added: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] `GOOGLE_OAUTH2_CLIENT_ID` set in Railway
- [ ] `GOOGLE_OAUTH2_CLIENT_SECRET` set in Railway

### GitHub OAuth:
- [ ] Callback URL set: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
- [ ] `GITHUB_CLIENT_ID` set in Railway
- [ ] `GITHUB_CLIENT_SECRET` set in Railway

### Django Site:
- [ ] Site domain updated to: `ai-resume-builder-jk.up.railway.app`

---

## 🔍 Troubleshooting

**If Google still shows "invalid_client":**
- Check Client ID in Railway (should start with numbers like `363779665485-...`)
- Verify redirect URI in Google Cloud Console matches exactly
- Make sure you clicked **SAVE** in Google Cloud Console

**If GitHub still shows "redirect_uri not associated":**
- Check callback URL in GitHub OAuth App matches exactly
- Make sure you clicked **"Update application"** in GitHub
- Verify Client ID and Secret are set in Railway

**If both still not working:**
- Verify Site model domain matches: `ai-resume-builder-jk.up.railway.app`
- Wait 2-3 minutes after changing Railway variables
- Clear browser cache and try again

---

## 📖 Detailed Guide

For detailed instructions, see: **[docs/OAUTH_COMPLETE_FIX.md](docs/OAUTH_COMPLETE_FIX.md)**

---

**Last Updated**: 2025

