# Security Warnings Fix Guide

This guide explains the security warnings from `python manage.py check --deploy` and how to fix them.

## ✅ What I've Fixed

I've added production security settings to `core/settings.py` that automatically enable when `DEBUG=False`. These settings are:

- ✅ **SECURE_SSL_REDIRECT** - Redirects HTTP to HTTPS
- ✅ **SECURE_HSTS_SECONDS** - HTTP Strict Transport Security (1 year)
- ✅ **SESSION_COOKIE_SECURE** - Secure session cookies (HTTPS only)
- ✅ **CSRF_COOKIE_SECURE** - Secure CSRF cookies (HTTPS only)
- ✅ **Additional security headers** - Content security, XSS protection, etc.

## 📋 Understanding the Warnings

### 1. SECURE_HSTS_SECONDS (W004)
**Warning**: HSTS not configured
**Status**: ✅ Fixed - Will be enabled in production (when DEBUG=False)
**Action**: No action needed - automatically handled

### 2. SECURE_SSL_REDIRECT (W008)
**Warning**: SSL redirect not enabled
**Status**: ✅ Fixed - Will be enabled in production
**Action**: No action needed - automatically handled

### 3. SECRET_KEY Warning (W009)
**Warning**: SECRET_KEY is too short or insecure
**Status**: ⚠️ Check your SECRET_KEY
**Action**: 
```bash
# Generate a new secure SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and update your `.env` file:
```
DJANGO_SECRET_KEY=your-generated-secret-key-here
```

### 4. SESSION_COOKIE_SECURE (W012)
**Warning**: Session cookies not secure
**Status**: ✅ Fixed - Will be enabled in production
**Action**: No action needed

### 5. CSRF_COOKIE_SECURE (W016)
**Warning**: CSRF cookies not secure
**Status**: ✅ Fixed - Will be enabled in production
**Action**: No action needed

### 6. DEBUG=True (W018)
**Warning**: DEBUG should be False in production
**Status**: ⚠️ Expected in development
**Action**: Set `DEBUG=False` in production (via Fly.io secrets)

### 7. ALLOWED_HOSTS Empty (W020)
**Warning**: ALLOWED_HOSTS is empty
**Status**: ⚠️ Expected in development
**Action**: Set `ALLOWED_HOSTS` in production (via Fly.io secrets)

## 🔧 For Production Deployment

### Set These Environment Variables in Fly.io:

```bash
# Critical Security
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com,yourapp.fly.dev"

# Generate and set SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
fly secrets set DJANGO_SECRET_KEY="your-generated-secret-key"

# CSRF Trusted Origins (if using custom domain)
fly secrets set CSRF_TRUSTED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com,https://yourapp.fly.dev"
```

## ✅ Verification

### In Development (Current):
These warnings are **expected** and **normal** for development. The security settings will automatically be enabled in production.

### In Production:
After deploying with `DEBUG=False` and proper `ALLOWED_HOSTS`, run:
```bash
fly ssh console -C "python manage.py check --deploy"
```

You should see **0 issues** (or only informational messages).

## 📝 Summary

**Current Status**:
- ✅ Security settings code added
- ✅ Will automatically enable in production
- ⚠️ Warnings are expected in development
- ⚠️ Need to set proper SECRET_KEY (if not already done)
- ⚠️ Need to set DEBUG=False and ALLOWED_HOSTS in production

**Next Steps**:
1. Verify your SECRET_KEY is secure (50+ characters, random)
2. Deploy to Fly.io with `DEBUG=False`
3. Set `ALLOWED_HOSTS` in Fly.io secrets
4. Verify no warnings in production

---

**Note**: These warnings are **normal for development**. They will be automatically resolved when you deploy with `DEBUG=False` and proper environment variables.

