# Fly.io Deployment Guide

Complete step-by-step guide to deploy AI Resume Builder on Fly.io (free tier available).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Account Setup](#account-setup)
3. [Project Initialization](#project-initialization)
4. [Database Setup](#database-setup)
5. [Redis Setup](#redis-setup)
6. [Celery Worker Configuration](#celery-worker-configuration)
7. [Environment Variables](#environment-variables)
8. [Static Files Configuration](#static-files-configuration)
9. [Media Files Setup](#media-files-setup)
10. [Deployment](#deployment)
11. [Post-Deployment](#post-deployment)
12. [Troubleshooting](#troubleshooting)
13. [Cost Estimation](#cost-estimation)

---

## Prerequisites

### Required Accounts
- [ ] Fly.io account (sign up at https://fly.io in browser)
- [ ] Google Cloud account (for Gemini API key)
- [ ] AWS account (optional, for S3 media storage)

### Required Tools (On Your Computer)
- [ ] Fly CLI installed (`flyctl` or `fly`) - **Installed on YOUR computer**
- [ ] Git installed - **On YOUR computer**
- [ ] Python 3.11+ installed locally (for testing) - **On YOUR computer**
- [ ] PowerShell or CMD - **On YOUR computer** (for running commands)

### ⚠️ Important: Where Commands Run

**All `fly` commands are run on YOUR COMPUTER (PowerShell/CMD), not in Fly.io console!**

- ✅ Create account: **Browser**
- ✅ Install Fly CLI: **Your Computer (PowerShell/CMD)**
- ✅ All deployment commands: **Your Computer (PowerShell/CMD)**
- ✅ Only SSH/Console: **After deployment** (for verification, optional)

### Install Fly CLI (On Your Computer)

**Open PowerShell or CMD on YOUR COMPUTER** and run:

**Windows (PowerShell)**:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**macOS/Linux (Terminal)**:
```bash
curl -L https://fly.io/install.sh | sh
```

**Verify Installation** (still in YOUR PowerShell/CMD):
```powershell
fly version
```

**Note**: Fly CLI is installed on YOUR computer and connects to Fly.io remotely.

---

## Account Setup

### 1. Create Fly.io Account (In Browser)

1. Go to https://fly.io in your **web browser**
2. Sign up with GitHub, Google, or email
3. Verify your email address
4. **Done!** ✅

### 2. Install Fly CLI (On Your Computer)

**Open PowerShell or CMD on YOUR COMPUTER** and run:

**Windows (PowerShell)**:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Verify Installation**:
```powershell
fly version
```

### 3. Login to Fly.io (On Your Computer)

**Still in YOUR PowerShell/CMD**, run:

```powershell
fly auth login
```

This will:
- Open your browser automatically
- Ask you to authorize the CLI
- Return to PowerShell/CMD when done

**Important**: All commands from now on are run on **YOUR COMPUTER** (PowerShell/CMD), not in Fly.io console!

---

## Project Initialization

**All commands below are run on YOUR COMPUTER (PowerShell/CMD)**

### 1. Navigate to Project Directory

**In YOUR PowerShell/CMD**, run:

```powershell
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"
```

### 2. Initialize Fly.io App

**Still in YOUR PowerShell/CMD**, run:

```powershell
fly launch
```

**During initialization, you'll be asked:**
- App name: Choose a unique name (e.g., `ai-resume-builder`)
- Region: Choose closest region (e.g., `iad` for US East)
- PostgreSQL: **Yes** (we'll set it up)
- Redis: **Yes** (we'll set it up)
- Deploy now: **No** (we need to configure first)

This creates a `fly.toml` configuration file.

### 3. Review fly.toml

The generated `fly.toml` will look something like this. We'll modify it:

```toml
app = "your-app-name"
primary_region = "iad"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

---

## Database Setup

### 1. Create Fly Postgres Database

```bash
fly postgres create --name ai-resume-builder-db --region iad --vm-size shared-cpu-1x --volume-size 3
```

**Note**: Free tier includes:
- 1 shared-cpu-1x VM (256MB RAM)
- 3GB storage
- Perfect for small to medium applications

### 2. Attach Database to App

```bash
fly postgres attach ai-resume-builder-db
```

This automatically:
- Sets `DATABASE_URL` environment variable
- Configures connection settings

### 3. Get Database Connection Details

```bash
fly postgres connect -a ai-resume-builder-db
```

Or get connection string:
```bash
fly secrets list | grep DATABASE_URL
```

### 4. Configure Database Settings

The `DATABASE_URL` is automatically set. Update your Django settings to use it:

**Option 1: Use dj-database-url (Recommended)**

Add to `requirements.txt`:
```
dj-database-url
```

Update `core/settings.py`:
```python
import dj_database_url

# Use DATABASE_URL if available, otherwise use existing logic
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
elif USE_POSTGRESQL:
    # Existing PostgreSQL config
    ...
```

**Option 2: Parse DATABASE_URL manually**

Extract connection details from `DATABASE_URL` and set individual variables.

---

## Redis Setup

### Option 1: Fly Redis (Recommended for Free Tier)

```bash
fly redis create --name ai-resume-builder-redis --region iad --vm-size shared-cpu-1x
```

**Attach to app**:
```bash
fly redis attach ai-resume-builder-redis
```

This automatically sets `REDIS_URL` environment variable.

### Option 2: External Redis (Redis Cloud Free Tier)

1. Sign up at https://redis.com/try-free/
2. Create free database
3. Get connection URL
4. Set in Fly.io:
```bash
fly secrets set CELERY_BROKER_URL="redis://your-redis-url"
fly secrets set CELERY_RESULT_BACKEND="redis://your-redis-url"
```

### Update Celery Configuration

Update `core/settings.py` to use `REDIS_URL`:

```python
# Use REDIS_URL if available, otherwise use default
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
```

---

## Celery Worker Configuration

### Option 1: Separate Process in Same App (Recommended for Free Tier)

Update `fly.toml` to include Celery worker process:

```toml
app = "your-app-name"
primary_region = "iad"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

# Web server process
[[services]]
  processes = ["app"]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

    [[services.ports.tls_options]]
      alpn = ["h2", "http/1.1"]
      default_version = "TLSv1.2"
      versions = ["TLSv1.2", "TLSv1.3"]

# Celery worker process
[[processes]]
  app = "celery-worker"
  command = "celery -A core worker -l info -P eventlet --concurrency=10"
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
  processes = ["celery-worker"]
```

### Option 2: Separate Fly.io App for Worker

Create a separate app for the Celery worker:

```bash
fly apps create ai-resume-builder-worker
fly deploy --app ai-resume-builder-worker
```

Configure worker app's `fly.toml` with only the Celery process.

---

## Environment Variables

**All commands below are run on YOUR COMPUTER (PowerShell/CMD)**

### Set All Required Secrets

**In YOUR PowerShell/CMD**, run:

```powershell
# Critical Security
fly secrets set DJANGO_SECRET_KEY="your-generated-secret-key"
fly secrets set DEBUG=False
fly secrets set ALLOWED_HOSTS="yourapp.fly.dev,yourdomain.com"

# Google AI
fly secrets set GOOGLE_AI_API_KEY="your-google-ai-api-key"
fly secrets set USE_GEMINI=True
fly secrets set GEMINI_MODEL="models/gemini-2.5-flash"

# Database (automatically set by fly postgres attach)
# DATABASE_URL is set automatically

# Redis (automatically set by fly redis attach)
# REDIS_URL is set automatically
# Or set manually:
# fly secrets set CELERY_BROKER_URL="redis://..."
# fly secrets set CELERY_RESULT_BACKEND="redis://..."

# Job Features (optional)
fly secrets set JOBS_FEATURE_ENABLED=False

# Logging
fly secrets set DJANGO_LOG_LEVEL=INFO
```

### Verify Secrets

```bash
fly secrets list
```

### Generate SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it in `fly secrets set DJANGO_SECRET_KEY="..."`.

---

## Static Files Configuration

### 1. Update settings.py

Ensure WhiteNoise is configured (already done):
```python
MIDDLEWARE = [
    ...
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 2. Create Dockerfile (if not exists)

Fly.io uses Docker. Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### 3. Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
db.sqlite3
media/
staticfiles/
.env
*.md
```

---

## Media Files Setup

**All commands below are run on YOUR COMPUTER (PowerShell/CMD)**

### Option 1: AWS S3 (Recommended for Production)

**Setup Steps** (mix of browser and your computer):

1. **Create S3 Bucket** (In AWS Console - Browser):
   - Go to AWS S3 Console
   - Create bucket (e.g., `ai-resume-builder-media`)
   - Configure CORS and permissions

2. **Create IAM User** (In AWS Console - Browser):
   - Create IAM user with S3 access
   - Generate access keys

3. **Install django-storages**:
   Already in `requirements.txt`

4. **Update settings.py**:
   ```python
   # Add to settings.py
   AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
   AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
   AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
   AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
   AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
   AWS_DEFAULT_ACL = 'public-read'
   
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
   ```

5. **Set AWS Secrets**:
   ```bash
   fly secrets set AWS_ACCESS_KEY_ID="your-access-key"
   fly secrets set AWS_SECRET_ACCESS_KEY="your-secret-key"
   fly secrets set AWS_STORAGE_BUCKET_NAME="your-bucket-name"
   fly secrets set AWS_S3_REGION_NAME="us-east-1"
   ```

### Option 2: Fly Volumes (Local Storage) - ⭐ Recommended for Starting

**In YOUR PowerShell/CMD**, run:

1. **Create Volume**:
   ```powershell
   fly volumes create media_data --size 3 --region iad
   ```

2. **Update fly.toml**:
   ```toml
   [[mounts]]
     source = "media_data"
     destination = "/app/media"
   ```

3. **Update settings.py**:
   ```python
   MEDIA_ROOT = '/app/media'
   MEDIA_URL = '/media/'
   ```

**Note**: Volumes are persistent but not shared across regions. S3 is recommended for production.

---

## Deployment

**All commands below are run on YOUR COMPUTER (PowerShell/CMD)**

### 1. Final Pre-Deployment Checks

- [ ] All migrations tested
- [ ] Static files collected locally
- [ ] Environment variables set
- [ ] Database and Redis connected
- [ ] `fly.toml` configured correctly

### 2. Deploy Application

**In YOUR PowerShell/CMD**, run:

```powershell
fly deploy
```

This will:
- Build Docker image
- Push to Fly.io
- Deploy application
- Run health checks

### 3. Run Migrations

After first deployment, **from YOUR PowerShell/CMD**, run:

```powershell
fly ssh console -C "python manage.py migrate"
```

Or add to Dockerfile CMD (already included).

### 4. Create Superuser

**From YOUR PowerShell/CMD**, run:

```powershell
fly ssh console -C "python manage.py createsuperuser"
```

**Note**: `fly ssh console` connects from YOUR computer to the Fly.io machine temporarily.

### 5. Verify Deployment

**All commands run from YOUR PowerShell/CMD**:

```powershell
# Check app status
fly status

# View logs
fly logs

# Open app in browser
fly open
```

---

## Post-Deployment

### 1. Verify All Features

- [ ] Home page loads
- [ ] User registration works
- [ ] User login works
- [ ] Resume builder works
- [ ] PDF generation works
- [ ] Admin dashboard accessible
- [ ] Bug reporting works
- [ ] Static files load correctly

### 2. Set Up Monitoring

```bash
# View real-time logs
fly logs

# Check app metrics
fly status

# SSH into app
fly ssh console
```

### 3. Configure Custom Domain (Optional)

```bash
# Add domain
fly certs add yourdomain.com

# Verify DNS
fly certs show yourdomain.com

# Update ALLOWED_HOSTS
fly secrets set ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com,yourapp.fly.dev"
```

### 4. Set Up Backups

Fly Postgres has automatic backups. Verify:
```bash
fly postgres backups list -a ai-resume-builder-db
```

### 5. Configure Health Checks

Update `fly.toml` with health check endpoint:

```toml
[http_service]
  internal_port = 8000
  force_https = true
  
  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/"
```

---

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Check logs**:
```bash
fly logs
```

**Common causes**:
- Missing environment variables
- Database connection issues
- Migration errors

**Solution**:
```bash
# Check secrets
fly secrets list

# Test database connection
fly ssh console -C "python manage.py dbshell"

# Run migrations manually
fly ssh console -C "python manage.py migrate"
```

#### 2. Static Files Not Loading

**Solution**:
```bash
# Collect static files
fly ssh console -C "python manage.py collectstatic --noinput"

# Verify STATIC_ROOT in settings
fly ssh console -C "python manage.py shell -c 'from django.conf import settings; print(settings.STATIC_ROOT)'"
```

#### 3. Celery Worker Not Running

**Check worker logs**:
```bash
fly logs --app your-app-name -p celery-worker
```

**Verify Redis connection**:
```bash
fly secrets list | grep REDIS
```

**Restart worker**:
```bash
fly apps restart your-app-name --process celery-worker
```

#### 4. Database Connection Errors

**Check DATABASE_URL**:
```bash
fly secrets list | grep DATABASE
```

**Test connection**:
```bash
fly postgres connect -a ai-resume-builder-db
```

#### 5. PDF Generation Fails

**Check WeasyPrint installation**:
```bash
fly ssh console -C "python -c 'import weasyprint; print(weasyprint.__version__)'"
```

**Install system dependencies in Dockerfile** (if needed):
```dockerfile
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

#### 6. Out of Memory Errors

**Increase memory in fly.toml**:
```toml
[[vm]]
  memory_mb = 512  # Increase from 256
```

**Note**: Free tier limit is 256MB per VM. Consider upgrading or optimizing.

---

## Cost Estimation

### Fly.io Free Tier Limits

**Included Free**:
- 3 shared-cpu-1x VMs (256MB RAM each)
- 3GB persistent volume storage
- 160GB outbound data transfer per month
- PostgreSQL database (shared-cpu-1x, 3GB storage)
- Redis (shared-cpu-1x)

### Estimated Monthly Cost: **$0** (Free Tier)

**Configuration**:
- Web server: 1 VM (256MB) - **Free**
- Celery worker: 1 VM (256MB) - **Free**
- PostgreSQL: 1 VM (256MB, 3GB storage) - **Free**
- Redis: 1 VM (256MB) - **Free**

### If You Exceed Free Tier

**Paid Options**:
- Additional VMs: ~$1.94/month per VM
- More memory: ~$0.002/GB-hour
- More storage: ~$0.15/GB-month
- More bandwidth: ~$0.02/GB

**Typical Paid Setup** (if needed):
- 2 VMs (512MB each): ~$3.88/month
- PostgreSQL (1GB RAM): ~$15/month
- Total: ~$19/month

---

## Alternative Platforms

### Railway.app (Free Tier Available)

Similar to Fly.io, Railway offers:
- Free tier with $5 credit/month
- PostgreSQL included
- Redis available
- Easy deployment

### Render.com

- Free tier for web services
- PostgreSQL free tier
- **Paid** for background workers (~$7/month)
- Easy setup

### DigitalOcean App Platform

- Free tier available
- PostgreSQL and Redis available
- More expensive than Fly.io

---

## Quick Reference Commands

```bash
# Deploy
fly deploy

# View logs
fly logs

# Check status
fly status

# SSH into app
fly ssh console

# Set secrets
fly secrets set KEY="value"

# List secrets
fly secrets list

# Remove secret
fly secrets unset KEY

# Scale app
fly scale count 2

# View metrics
fly metrics

# Open app
fly open

# Restart app
fly apps restart

# View database
fly postgres connect -a ai-resume-builder-db

# View Redis
fly redis connect -a ai-resume-builder-redis
```

---

## Step-by-Step Deployment Summary

1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
2. **Login**: `fly auth login`
3. **Initialize**: `fly launch`
4. **Create Database**: `fly postgres create --name ai-resume-builder-db`
5. **Attach Database**: `fly postgres attach ai-resume-builder-db`
6. **Create Redis**: `fly redis create --name ai-resume-builder-redis`
7. **Attach Redis**: `fly redis attach ai-resume-builder-redis`
8. **Set Secrets**: `fly secrets set DJANGO_SECRET_KEY="..." DEBUG=False ...`
9. **Update fly.toml**: Add Celery worker process
10. **Deploy**: `fly deploy`
11. **Run Migrations**: `fly ssh console -C "python manage.py migrate"`
12. **Create Superuser**: `fly ssh console -C "python manage.py createsuperuser"`
13. **Verify**: `fly open`

---

**Last Updated**: 2025
**Platform**: Fly.io
**Status**: Ready for Deployment

