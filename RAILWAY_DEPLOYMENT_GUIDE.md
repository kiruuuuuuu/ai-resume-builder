# Railway.app Deployment Guide

Complete step-by-step guide to deploy AI Resume Builder on Railway.app (FREE tier - no payment method required!).

## 🎉 Why Railway.app?

- ✅ **FREE Tier**: $5/month credit (no payment method required)
- ✅ **Free PostgreSQL**: Included in free tier
- ✅ **Free Redis**: Available
- ✅ **Easy Setup**: Deploy in minutes
- ✅ **No Credit Card Required**: For free tier

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Account Setup](#account-setup)
3. [Project Setup](#project-setup)
4. [Database Setup](#database-setup)
5. [Redis Setup](#redis-setup)
6. [Environment Variables](#environment-variables)
7. [Deployment](#deployment)
8. [Post-Deployment](#post-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- [ ] Railway.app account (sign up at https://railway.app - FREE, no payment method needed)
- [ ] Google Cloud account (for Gemini API key)
- [ ] GitHub account (to connect your repository)

### Required Tools
- [ ] Git installed on your computer
- [ ] Python 3.11+ installed locally (for testing)

---

## Account Setup

### 1. Create Railway.app Account

1. Go to https://railway.app in your browser
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email
4. **No payment method required!** ✅

### 2. Install Railway CLI (Optional but Recommended)

**Windows (PowerShell)**:
```powershell
# Install via npm (if you have Node.js)
npm install -g @railway/cli

# Or download from: https://github.com/railwayapp/cli/releases
```

**Verify Installation**:
```powershell
railway --version
```

---

## Project Setup

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```powershell
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **In Railway Dashboard**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository: `ai-resume-builder`
   - Railway will automatically detect Django and set up the project

### Option 2: Deploy from Local Directory

1. **Login to Railway**:
   ```powershell
   railway login
   ```

2. **Initialize Railway in your project**:
   ```powershell
   cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"
   railway init
   ```

3. **Link to existing project or create new**:
   - Follow the prompts to create a new project

---

## Database Setup

### 1. Add PostgreSQL Service

**In Railway Dashboard**:
1. Click on your project
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway automatically creates a PostgreSQL database
4. **It's FREE!** ✅

### 2. Get Database Connection String

**In Railway Dashboard**:
1. Click on the PostgreSQL service
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` (automatically set)
4. Or copy individual variables:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

### 3. Configure Django Settings

Railway automatically sets `DATABASE_URL`. Update your `core/settings.py`:

```python
import dj_database_url
import os

# Use DATABASE_URL if available (Railway sets this automatically)
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Development SQLite fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## Redis Setup

### 1. Add Redis Service

**In Railway Dashboard**:
1. Click on your project
2. Click "New" → "Database" → "Add Redis"
3. Railway automatically creates a Redis instance
4. **It's FREE!** ✅

### 2. Get Redis Connection String

**In Railway Dashboard**:
1. Click on the Redis service
2. Go to "Variables" tab
3. Copy the `REDIS_URL` (automatically set)

### 3. Configure Celery

Your `core/settings.py` already has Celery configuration. Railway automatically sets `REDIS_URL`, so Celery will work automatically!

**Verify Celery settings in `core/settings.py`** (should already be there):
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'))
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'))
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

**Note**: Railway runs on Linux, so Celery will automatically use `eventlet` pool for better concurrency (your code already handles this).

---

## Environment Variables

### Set Environment Variables in Railway

**In Railway Dashboard**:
1. Click on your Django service
2. Go to "Variables" tab
3. Click "New Variable"
4. Add these variables:

#### Critical Security Variables

```
DJANGO_SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app,your-custom-domain.com
```

#### AI Features

```
GOOGLE_AI_API_KEY=your-google-ai-api-key
USE_GEMINI=True
GEMINI_MODEL=models/gemini-2.5-flash
```

#### Celery Configuration (Auto-set from Redis)

Railway automatically sets these when you add Redis:
```
REDIS_URL=redis://... (automatically set)
CELERY_BROKER_URL=redis://... (can use REDIS_URL or set separately)
CELERY_RESULT_BACKEND=redis://... (can use REDIS_URL or set separately)
```

**Note**: You can reference `REDIS_URL` in Celery settings, or set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` separately if needed.

#### Optional

```
JOBS_FEATURE_ENABLED=False
DJANGO_LOG_LEVEL=INFO
CSRF_TRUSTED_ORIGINS=https://*.railway.app
```

### Generate SECRET_KEY

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `DJANGO_SECRET_KEY`.

---

## Deployment

### 1. Configure Railway Settings

**Create `railway.toml`** (optional, Railway auto-detects Django):

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 2. Update Django Settings for Railway

**Update `core/settings.py`**:

```python
import os

# Railway automatically sets PORT
PORT = os.getenv('PORT', '8000')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Railway provides persistent storage)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*.railway.app').split(',')

# Security (production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### 3. Update requirements.txt

Ensure you have:

```
gunicorn
dj-database-url
whitenoise
```

### 4. Create Procfile (Optional)

Create `Procfile` in project root:

```
web: python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A core worker -l info
```

### 5. Deploy

**Option A: Automatic Deploy from GitHub**
- Railway automatically deploys when you push to GitHub
- Just push your code:
  ```powershell
  git add .
  git commit -m "Deploy to Railway"
  git push origin main
  ```

**Option B: Deploy via CLI**
```powershell
railway up
```

### 6. Run Migrations

**In Railway Dashboard**:
1. Click on your Django service
2. Go to "Deployments" tab
3. Click on the latest deployment
4. Click "View Logs"
5. Or use Railway CLI:
   ```powershell
   railway run python manage.py migrate
   ```

### 7. Create Superuser

**Using Railway CLI**:
```powershell
railway run python manage.py createsuperuser
```

Or use Railway's web terminal in the dashboard.

---

## Post-Deployment

### 1. Get Your App URL

**In Railway Dashboard**:
1. Click on your Django service
2. Go to "Settings" tab
3. Click "Generate Domain"
4. Copy your app URL (e.g., `https://ai-resume-builder-production.up.railway.app`)

### 2. Update ALLOWED_HOSTS

Add your Railway domain to `ALLOWED_HOSTS`:
```
ALLOWED_HOSTS=*.railway.app,your-app-name.up.railway.app
```

### 3. Verify Deployment

1. Visit your app URL
2. Test:
   - Home page loads
   - User registration works
   - Resume builder works
   - PDF generation works

### 4. Set Up Custom Domain (Optional)

**In Railway Dashboard**:
1. Click on your service
2. Go to "Settings" → "Domains"
3. Click "Custom Domain"
4. Add your domain
5. Update DNS records as instructed

---

## Celery Worker Setup

Your app uses Celery for async tasks like:
- PDF generation
- Resume parsing
- Resume scoring

### Option 1: Separate Service (Recommended for Production) ✅

**In Railway Dashboard**:
1. Click on your project
2. Click "New" → "Empty Service"
3. Name it "celery-worker"
4. Connect to the same GitHub repository
5. Go to "Settings" → "Deploy"
6. Set "Start Command":
   ```
   celery -A core worker -l info -P eventlet --concurrency=10
   ```
   **Note**: Railway runs on Linux, so we use `eventlet` pool for better performance.

7. **Add Environment Variables** (same as main service):
   - Go to "Variables" tab
   - Add all the same variables as your Django service:
     - `DJANGO_SECRET_KEY`
     - `DEBUG`
     - `ALLOWED_HOSTS`
     - `GOOGLE_AI_API_KEY`
     - `DATABASE_URL` (from PostgreSQL service)
     - `REDIS_URL` (from Redis service)
     - `CELERY_BROKER_URL` (can use `REDIS_URL`)
     - `CELERY_RESULT_BACKEND` (can use `REDIS_URL`)

8. **Link to Redis Service**:
   - Go to "Variables" tab
   - Click "Reference Variable"
   - Select Redis service
   - Select `REDIS_URL`
   - This automatically sets `REDIS_URL` for the worker

9. **Link to PostgreSQL Service**:
   - Go to "Variables" tab
   - Click "Reference Variable"
   - Select PostgreSQL service
   - Select `DATABASE_URL`
   - This automatically sets `DATABASE_URL` for the worker

**Verify Worker is Running**:
1. Go to "Deployments" tab
2. Check logs - you should see:
   ```
   celery@v1 ready.
   ```

### Option 2: Single Service with Procfile (For Testing)

If you want to run both web and worker in one service (uses more resources):

1. **Create `Procfile`** in project root:
   ```
   web: python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
   worker: celery -A core worker -l info -P eventlet --concurrency=10
   ```

2. **Update Railway Service**:
   - Go to "Settings" → "Deploy"
   - Set "Start Command" to: `railway run`
   - Railway will run both processes from Procfile

**Note**: Option 1 (separate service) is recommended for production as it allows better scaling and resource management.

### Verify Celery is Working

**Check Worker Logs**:
1. Go to celery-worker service
2. Click "Deployments" → "View Logs"
3. You should see:
   ```
   [INFO] celery@v1 ready.
   ```

**Test Celery Task**:
1. Use your app to generate a PDF
2. Check worker logs - you should see task execution
3. Check Django service logs for task completion

### Celery Configuration Notes

- **Railway runs on Linux**: Your code automatically uses `eventlet` pool (better concurrency)
- **Redis Connection**: Automatically configured via `REDIS_URL` from Railway
- **Task Serialization**: Uses JSON (already configured)
- **Concurrency**: Set to 10 workers (adjust based on your needs)

---

## Troubleshooting

### Application Won't Start

**Check Logs**:
1. In Railway Dashboard → Your service → "Deployments" → "View Logs"
2. Look for errors

**Common Issues**:
- Missing environment variables
- Database connection errors
- Migration errors

**Fix**:
```powershell
# Check environment variables
railway variables

# Run migrations
railway run python manage.py migrate

# Check Django settings
railway run python manage.py check
```

### Static Files Not Loading

**Solution**:
1. Ensure `whitenoise` is in `requirements.txt`
2. Add to `MIDDLEWARE`:
   ```python
   'whitenoise.middleware.WhiteNoiseMiddleware',
   ```
3. Collect static files:
   ```powershell
   railway run python manage.py collectstatic --noinput
   ```

### Database Connection Errors

**Check**:
1. Railway Dashboard → PostgreSQL service → "Variables"
2. Verify `DATABASE_URL` is set
3. Check Django service has access to PostgreSQL

### Celery Worker Not Running

**Symptoms**:
- PDF generation not working
- Tasks not being processed
- Worker service not starting

**Solutions**:

1. **Check Worker Service Logs**:
   - Go to celery-worker service → "Deployments" → "View Logs"
   - Look for errors

2. **Verify Redis Connection**:
   ```powershell
   # Check if REDIS_URL is set
   railway variables --service celery-worker
   ```
   - Should show `REDIS_URL` from Redis service

3. **Verify Environment Variables**:
   - Worker service needs same variables as Django service
   - Especially: `DATABASE_URL`, `REDIS_URL`, `DJANGO_SECRET_KEY`

4. **Check Start Command**:
   - Should be: `celery -A core worker -l info -P eventlet --concurrency=10`
   - Verify in "Settings" → "Deploy"

5. **Test Redis Connection**:
   ```powershell
   # In Railway CLI
   railway run --service celery-worker python -c "import os; print(os.getenv('REDIS_URL'))"
   ```

6. **Restart Worker Service**:
   - Go to celery-worker service
   - Click "Deployments" → "Redeploy"

**Common Issues**:
- Missing `REDIS_URL`: Link Redis service to worker
- Missing `DATABASE_URL`: Link PostgreSQL service to worker
- Wrong start command: Use `-P eventlet` for Railway (Linux)
- Worker service not created: Create separate service for worker

---

## Cost Estimation

### Railway Free Tier

**Included FREE**:
- $5/month credit
- PostgreSQL database (included)
- Redis (included)
- 500 hours of usage/month
- 100GB bandwidth/month

### Estimated Monthly Cost: **$0** (Free Tier)

**Configuration**:
- Web service: ~$0-5/month (within free credit)
- PostgreSQL: FREE (included)
- Redis: FREE (included)
- Celery worker: ~$0-5/month (within free credit)

**Total**: **$0/month** if you stay within free tier limits!

---

## Quick Reference Commands

```powershell
# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# View logs
railway logs

# Run commands
railway run python manage.py migrate
railway run python manage.py createsuperuser

# View variables
railway variables

# Open app
railway open
```

---

## Summary

**Railway.app is perfect for free deployment because**:
- ✅ No payment method required for free tier
- ✅ Free PostgreSQL included
- ✅ Free Redis included
- ✅ $5/month credit (enough for small apps)
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ Simple setup

**Next Steps**:
1. Create Railway account (no payment needed)
2. Connect GitHub repository
3. Add PostgreSQL and Redis services
4. Set environment variables
5. Deploy!

---

**Last Updated**: 2025  
**Platform**: Railway.app  
**Status**: FREE Tier Available (No Payment Method Required!)

