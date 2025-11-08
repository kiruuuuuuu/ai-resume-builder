# Environment Variables Guide

Complete guide for all environment variables needed for AI Resume Builder deployment.

## 🔑 Required Environment Variables

### 1. DJANGO_SECRET_KEY (CRITICAL) ⚠️

**Required**: YES - Application will not start without this  
**Generate**: 
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example**:
```
DJANGO_SECRET_KEY=django-insecure-your-very-long-random-secret-key-here
```

**Where to set**:
- Development: `.env` file (never commit to Git!)
- Production: Fly.io secrets (`fly secrets set DJANGO_SECRET_KEY="..."`)

---

### 2. DEBUG

**Required**: YES  
**Default**: `True` (development)  
**Production**: Must be `False`

**Example**:
```
DEBUG=False
```

**Where to set**:
- Development: `.env` file
- Production: Fly.io secrets (`fly secrets set DEBUG=False`)

**Note**: Security settings automatically enable when `DEBUG=False`

---

### 3. ALLOWED_HOSTS

**Required**: YES (in production)  
**Format**: Comma-separated list of domains

**Example**:
```
ALLOWED_HOSTS=yourapp.fly.dev,yourdomain.com,www.yourdomain.com
```

**Where to set**:
- Development: Leave empty or use `localhost,127.0.0.1`
- Production: Fly.io secrets (`fly secrets set ALLOWED_HOSTS="yourapp.fly.dev,yourdomain.com"`)

**Note**: Include your Fly.io app URL and any custom domains

---

### 4. GOOGLE_AI_API_KEY

**Required**: YES (if using Gemini AI features)  
**Get from**: https://aistudio.google.com/app/apikey

**Example**:
```
GOOGLE_AI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr
```

**Where to set**:
- Development: `.env` file
- Production: Fly.io secrets (`fly secrets set GOOGLE_AI_API_KEY="..."`)

---

## 🔵 Database Environment Variables (PostgreSQL)

### 5. USE_POSTGRESQL

**Required**: YES (for production)  
**Default**: `False` (uses SQLite in development)

**Example**:
```
USE_POSTGRESQL=True
```

---

### 6-10. Database Connection (From Fly Postgres)

These will be automatically set by Fly.io when you attach a Postgres database:

- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host (usually `*.flycast` or `*.internal`)
- `DB_PORT` - Database port (usually `5432`)

**How to get**: After creating Fly Postgres, run:
```bash
fly postgres connect -a your-db-app-name
```

**Or set manually**:
```bash
fly secrets set \
  DB_NAME=your_db_name \
  DB_USER=your_db_user \
  DB_PASSWORD=your_db_password \
  DB_HOST=your_db_host \
  DB_PORT=5432
```

---

## 🟢 Redis/Celery Environment Variables

### 11-12. Celery Configuration

**Required**: YES (if using Celery for async tasks)

- `CELERY_BROKER_URL` - Redis connection URL for Celery broker
- `CELERY_RESULT_BACKEND` - Redis connection URL for Celery results

**Example** (Fly Redis):
```
CELERY_BROKER_URL=redis://default:your-redis-password@your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://default:your-redis-password@your-redis-host:6379/0
```

**How to get**: After creating Fly Redis, the connection string is provided

**Set in Fly.io**:
```bash
fly secrets set \
  CELERY_BROKER_URL="redis://..." \
  CELERY_RESULT_BACKEND="redis://..."
```

---

## 🟡 Optional Environment Variables

### 13. CSRF_TRUSTED_ORIGINS

**Required**: NO (only if using custom domain)  
**Format**: Comma-separated list of HTTPS URLs

**Example**:
```
CSRF_TRUSTED_ORIGINS=https://yourapp.fly.dev,https://yourdomain.com,https://www.yourdomain.com
```

**Where to set**:
- Production: Fly.io secrets (`fly secrets set CSRF_TRUSTED_ORIGINS="https://yourapp.fly.dev"`)

---

### 14. USE_GEMINI

**Required**: NO  
**Default**: `True`

**Example**:
```
USE_GEMINI=True
```

**Set to `False` to disable all Gemini AI features**

---

### 15. GEMINI_MODEL

**Required**: NO  
**Default**: `models/gemini-2.5-flash`

**Example**:
```
GEMINI_MODEL=models/gemini-2.5-flash
```

**Other options**: `models/gemini-pro`, `models/gemini-1.5-pro`, etc.

---

### 16. JOBS_FEATURE_ENABLED

**Required**: NO  
**Default**: `False` (job features are disabled by default)

**Example**:
```
JOBS_FEATURE_ENABLED=False
```

**Set to `True` to enable job features (remove "Coming Soon" banner)**

---

### 17. DJANGO_LOG_LEVEL

**Required**: NO  
**Default**: `INFO`

**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Example**:
```
DJANGO_LOG_LEVEL=INFO
```

---

### 18-21. AWS S3 Configuration (Optional - for media files)

**Required**: NO (only if using S3 for media storage)

- `USE_S3=True` - Enable S3 storage
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_STORAGE_BUCKET_NAME` - S3 bucket name
- `AWS_S3_REGION_NAME` - AWS region (e.g., `us-east-1`)

**Example**:
```
USE_S3=True
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=my-resume-builder-media
AWS_S3_REGION_NAME=us-east-1
```

**Note**: If not using S3, media files will be stored on Fly volumes

---

## 📋 Complete Environment Variables List

### For Development (.env file)

Create a `.env` file in your project root:

```env
# Critical Security
DJANGO_SECRET_KEY=your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Features
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
USE_GEMINI=True
GEMINI_MODEL=models/gemini-2.5-flash

# Database (Development - SQLite by default)
USE_POSTGRESQL=False

# Celery (Development - Redis local)
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Optional
JOBS_FEATURE_ENABLED=False
DJANGO_LOG_LEVEL=INFO
```

### For Production (Fly.io secrets)

Set these using Fly.io secrets:

```bash
# Critical Security
fly secrets set DJANGO_SECRET_KEY="your-generated-secret-key"
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS="yourapp.fly.dev,yourdomain.com"

# AI Features
fly secrets set GOOGLE_AI_API_KEY="your-google-ai-api-key"
fly secrets set USE_GEMINI=True
fly secrets set GEMINI_MODEL="models/gemini-2.5-flash"

# Database (from Fly Postgres - auto-set or manual)
fly secrets set USE_POSTGRESQL=True
fly secrets set DB_NAME="your_db_name"
fly secrets set DB_USER="your_db_user"
fly secrets set DB_PASSWORD="your_db_password"
fly secrets set DB_HOST="your_db_host"
fly secrets set DB_PORT="5432"

# Celery (from Fly Redis - auto-set or manual)
fly secrets set CELERY_BROKER_URL="redis://..."
fly secrets set CELERY_RESULT_BACKEND="redis://..."

# Optional
fly secrets set CSRF_TRUSTED_ORIGINS="https://yourapp.fly.dev"
fly secrets set JOBS_FEATURE_ENABLED=False
fly secrets set DJANGO_LOG_LEVEL=INFO
```

---

## 🔧 How to Generate/Get Values

### 1. Generate SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Output**: Copy the generated key and use it as `DJANGO_SECRET_KEY`

### 2. Get GOOGLE_AI_API_KEY

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Use it as `GOOGLE_AI_API_KEY`

### 3. Get Database Credentials (Fly Postgres)

After creating Fly Postgres:
```bash
# View connection details
fly postgres connect -a your-db-app-name

# Or get connection string
fly postgres connect -a your-db-app-name --command "echo $DATABASE_URL"
```

### 4. Get Redis Credentials (Fly Redis)

After creating Fly Redis:
```bash
# View connection details
fly redis connect -a your-redis-app-name
```

---

## ✅ Quick Checklist

### Must Have (Critical):
- [ ] `DJANGO_SECRET_KEY` - Generate using command above
- [ ] `DEBUG=False` - Set to False in production
- [ ] `ALLOWED_HOSTS` - Set your domain(s)
- [ ] `GOOGLE_AI_API_KEY` - Get from Google AI Studio

### Should Have (Important):
- [ ] `USE_POSTGRESQL=True` - Enable PostgreSQL
- [ ] Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- [ ] `CELERY_BROKER_URL` - Redis connection for Celery
- [ ] `CELERY_RESULT_BACKEND` - Redis connection for Celery results

### Nice to Have (Optional):
- [ ] `CSRF_TRUSTED_ORIGINS` - If using custom domain
- [ ] `USE_GEMINI` - Default True
- [ ] `GEMINI_MODEL` - Default models/gemini-2.5-flash
- [ ] `JOBS_FEATURE_ENABLED` - Default False
- [ ] `DJANGO_LOG_LEVEL` - Default INFO
- [ ] AWS S3 credentials (if using S3)

---

## 🚀 Quick Start Commands

### Generate All Required Keys

```bash
# 1. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print('DJANGO_SECRET_KEY=' + get_random_secret_key())"

# 2. Get GOOGLE_AI_API_KEY from https://aistudio.google.com/app/apikey

# 3. Database and Redis credentials from Fly.io after creating resources
```

### Set All Secrets at Once (Fly.io)

```bash
fly secrets set \
  DJANGO_SECRET_KEY="your-secret-key" \
  DEBUG=False \
  ALLOWED_HOSTS="yourapp.fly.dev" \
  GOOGLE_AI_API_KEY="your-api-key" \
  USE_POSTGRESQL=True \
  USE_GEMINI=True \
  JOBS_FEATURE_ENABLED=False
```

---

## 📝 Notes

1. **Never commit `.env` file** - Add to `.gitignore`
2. **SECRET_KEY is critical** - Generate a new one for production
3. **Database credentials** - Fly.io can auto-set these when you attach Postgres
4. **Redis credentials** - Fly.io can auto-set these when you attach Redis
5. **Test locally first** - Use `.env` file for development
6. **Use Fly.io secrets** - Never hardcode secrets in code

---

## 🔍 Verify Environment Variables

### Check in Development

```bash
# Check .env file exists
ls -la .env

# Test environment variables are loaded
python manage.py shell
>>> import os
>>> from django.conf import settings
>>> settings.SECRET_KEY  # Should show your secret key
>>> settings.DEBUG  # Should show True/False
```

### Check in Production (Fly.io)

```bash
# List all secrets
fly secrets list

# SSH into app and check
fly ssh console
python manage.py shell
>>> from django.conf import settings
>>> settings.SECRET_KEY  # Should show your secret key
>>> settings.DEBUG  # Should show False
```

---

**Last Updated**: 2025

