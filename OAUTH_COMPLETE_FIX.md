# Complete OAuth Fix for Google & GitHub

Both Google and GitHub OAuth are failing because **redirect URIs are not configured**. Here's how to fix both:

## 🔴 Current Issues

1. **Google**: "invalid_client" error - Client ID has `http://` prefix OR redirect URI not added
2. **GitHub**: "redirect_uri is not associated with this application" - Redirect URI not added in GitHub OAuth app

## ✅ Fix for Google OAuth

### Step 1: Verify Client ID in Railway

1. Go to **Railway Dashboard** → Your Service → **Variables**
2. Find `GOOGLE_OAUTH2_CLIENT_ID`
3. **It MUST be the complete Client ID** (check Google Cloud Console for the full value)
   - ❌ Should NOT have `http://` or `https://` prefix
   - ✅ Just the Client ID itself (ends with `.apps.googleusercontent.com`)
   - ❌ **NO** `http://` or `https://` prefix
   - ✅ Just the Client ID itself
4. If it's wrong, edit it and paste the correct value
5. Save

### Step 2: Add Redirect URI in Google Cloud Console

**THIS IS CRITICAL!**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID (the one you created)
4. Click **Edit** (pencil icon)
5. Scroll to **Authorized redirect URIs**
6. Click **+ ADD URI**
7. Add this **EXACT** URI:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
   ```
8. **Click SAVE** (very important!)

### Step 3: Verify Client Secret

1. In Railway Dashboard → Variables
2. Find `GOOGLE_OAUTH2_CLIENT_SECRET`
3. Should match the Client Secret from Google Cloud Console
4. If different, update it

---

## ✅ Fix for GitHub OAuth

### Step 1: Get GitHub Client ID and Secret

From the error, I can see your GitHub Client ID is: `Ov23licsLetCTcqewu8B`

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click on your OAuth App (or create a new one)
3. Copy the **Client ID** and **Client Secret**

### Step 2: Add Redirect URI in GitHub OAuth App

**THIS IS CRITICAL!**

1. In GitHub Developer Settings → Your OAuth App
2. Find **Authorization callback URL**
3. Add this **EXACT** URL:
   ```
   https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/
   ```
4. **Click "Update application"** (very important!)

### Step 3: Verify Railway Variables

1. Go to **Railway Dashboard** → Your Service → **Variables**
2. Verify these are set:
   - `GITHUB_CLIENT_ID` = Your GitHub Client ID (check GitHub Developer Settings)
   - `GITHUB_CLIENT_SECRET` = Your GitHub Client Secret
3. If missing or incorrect, add/update them
4. Save

---

## ✅ Update Django Site Model

Both OAuth providers need the Site model to be correctly configured:

1. Run this command:
   ```bash
   conda activate resume_env
   railway run python manage.py shell
   ```

2. In the Python shell:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ai-resume-builder-jk.up.railway.app'
   site.name = 'AI Resume Builder'
   site.save()
   print(f"✅ Site updated: {site.domain}")
   exit()
   ```

---

## 📋 Complete Checklist

### Google OAuth:
- [ ] Client ID in Railway: Complete Client ID from Google Cloud Console (no `http://` prefix)
- [ ] Client Secret in Railway: Client Secret from Google Cloud Console
- [ ] Redirect URI added in Google Cloud Console: `https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/`
- [ ] Saved changes in Google Cloud Console

### GitHub OAuth:
- [ ] Client ID in Railway: Your GitHub Client ID (check GitHub Developer Settings)
- [ ] Client Secret in Railway: Your GitHub Client Secret
- [ ] Redirect URI added in GitHub OAuth App: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
- [ ] Saved changes in GitHub (clicked "Update application")

### Django Site Model:
- [ ] Site domain updated to: `ai-resume-builder-jk.up.railway.app`
- [ ] Site name updated to: `AI Resume Builder`

---

## 🧪 Testing

1. **Wait 2-3 minutes** for Railway to redeploy after variable changes
2. Go to: https://ai-resume-builder-jk.up.railway.app/
3. Click **Login**
4. Try **Sign in with Google** - should redirect to Google (not show error)
5. Try **Sign in with GitHub** - should redirect to GitHub (not show error)

---

## 🔍 Troubleshooting

### Still getting Google "invalid_client" error?
1. Check Railway variables - Client ID should NOT have `http://` prefix
2. Verify redirect URI in Google Cloud Console matches exactly
3. Make sure you clicked **SAVE** in Google Cloud Console
4. Wait a few minutes for changes to propagate

### Still getting GitHub "redirect_uri not associated" error?
1. Check GitHub OAuth App settings - redirect URI must match exactly
2. Verify redirect URI: `https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/`
3. Make sure you clicked **"Update application"** in GitHub
4. Wait a few minutes for changes to propagate

### Both still not working?
1. Verify Site model domain: `ai-resume-builder-jk.up.railway.app`
2. Check Railway logs: `railway logs`
3. Verify all environment variables are set correctly
4. Make sure Railway has redeployed after changes

---

## 🎯 Quick Reference

**Your Railway Domain:** `ai-resume-builder-jk.up.railway.app`

**Google Redirect URI:**
```
https://ai-resume-builder-jk.up.railway.app/accounts/google/login/callback/
```

**GitHub Redirect URI:**
```
https://ai-resume-builder-jk.up.railway.app/accounts/github/login/callback/
```

**Where to configure:**
- Google: [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
- GitHub: [GitHub Developer Settings](https://github.com/settings/developers) → Your OAuth App

