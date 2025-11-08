# Fix "Bad Request (400)" Error on Railway

## ❌ Problem

You're getting a "Bad Request (400)" error when accessing your Railway app URL:
```
https://ai-resume-builder-jk.up.railway.app
```

**Error**: `Bad Request (400)`

## 🔍 Root Cause

This error occurs because Django's `ALLOWED_HOSTS` setting doesn't include your Railway domain. Django requires `ALLOWED_HOSTS` to be set in production (`DEBUG=False`) for security reasons.

## ✅ Solution

### Option 1: Automatic Fix (Recommended) ⭐

**The code has been updated to automatically allow Railway domains!**

Just **redeploy your service** and it should work:

1. **The fix is in the code** - `core/settings.py` now automatically allows Railway domains
2. **Railway will auto-redeploy** after the git push
3. **Or manually redeploy**: Go to Railway Dashboard → Deployments → Redeploy

**After redeploy, your app should work!**

### Option 2: Set ALLOWED_HOSTS Environment Variable (Manual)

If you want to set it manually:

1. **Go to Railway Dashboard**
2. **Click on your Django app service**
3. **Go to "Variables" tab**
4. **Add new variable**:
   - **Name**: `ALLOWED_HOSTS`
   - **Value**: `ai-resume-builder-jk.up.railway.app`
   - Or use: `*.railway.app,*.up.railway.app` (but this won't work - see Option 1)

5. **Redeploy** the service

## 🔧 What Was Fixed

### Code Changes

**Before**:
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []
```

**After**:
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# Automatically allow Railway domains if ALLOWED_HOSTS is not set and in production
if not ALLOWED_HOSTS and not DEBUG:
    ALLOWED_HOSTS = ['.railway.app', '.up.railway.app']
```

**Also fixed CSRF_TRUSTED_ORIGINS**:
```python
# Automatically allow Railway HTTPS origins for CSRF
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']
```

## 📝 How Django Domain Patterns Work

Django supports leading dots in `ALLOWED_HOSTS`:
- `.railway.app` - Matches all subdomains of `railway.app`
- `.up.railway.app` - Matches all subdomains of `up.railway.app`
- `ai-resume-builder-jk.up.railway.app` - Matches only this specific domain

**Your URL**: `ai-resume-builder-jk.up.railway.app` will match both:
- `.railway.app` ✅
- `.up.railway.app` ✅

## ✅ After the Fix

After redeploying, your app should:

1. **Load correctly** at `https://ai-resume-builder-jk.up.railway.app`
2. **Show your homepage** (not 400 error)
3. **Allow login/registration**
4. **Work with all features**

## 🧪 Test the Fix

After redeploy:

1. **Visit your URL**: `https://ai-resume-builder-jk.up.railway.app`
2. **You should see**: Your homepage (not 400 error)
3. **Test pages**:
   - Home: `https://ai-resume-builder-jk.up.railway.app/`
   - Login: `https://ai-resume-builder-jk.up.railway.app/accounts/login/`
   - Admin: `https://ai-resume-builder-jk.up.railway.app/users/admin-login/`

## 🔍 Verify the Fix

**Check Railway Logs**:

After redeploy, check logs for:
```
Starting server...
Booting worker with pid: ...
```

**No errors** about `ALLOWED_HOSTS` or `DisallowedHost`.

## 🎯 Summary

**Problem**: `ALLOWED_HOSTS` not set → Django rejects requests → 400 error

**Solution**: Code now automatically allows Railway domains (`.railway.app`, `.up.railway.app`)

**Action**: Redeploy your service (automatic after git push, or manually)

**Result**: Your app will work at `https://ai-resume-builder-jk.up.railway.app` ✅

---

**The fix is committed and pushed. Just wait for Railway to redeploy, or manually redeploy!** 🚀

