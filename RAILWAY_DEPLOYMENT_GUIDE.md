# Railway.app Deployment Guide

Complete step-by-step guide to deploy AI Resume Builder on Railway.app (FREE tier - no payment method required!).

## 🎉 Why Railway.app?

- ✅ **FREE Tier**: $1/month credit + $5 initial bonus (no payment method required)
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
8. [Post-Deployment Checklist](#post-deployment-checklist)
9. [Celery Worker Setup](#celery-worker-setup)
10. [Troubleshooting](#troubleshooting)
11. [Cost Estimation](#cost-estimation)

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
   - **If stuck on "Loading..."**:
     - Click "Configure GitHub App" button
     - Authorize Railway to access your GitHub repositories
     - Grant necessary permissions
     - Return to Railway and refresh the page
   - Select your repository: `ai-resume-builder`
   - Railway will automatically detect Django and set up the project

**Troubleshooting "Loading..." Issue**:
1. **Click "Configure GitHub App"** button (gear icon)
2. **Authorize Railway** in the GitHub authorization page
3. **Grant permissions** (read access to repositories)
4. **Return to Railway** and refresh the page
5. **Try again** - repositories should now load

**Alternative**: If still stuck, use Option 2 (CLI method) below.

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

**Note**: Railway runs on Linux. We use `prefork` pool (default) for stability with Redis. For higher concurrency, you can use `-P threads --concurrency=10` in the start command.

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

**⚠️ CRITICAL: Setting DJANGO_SECRET_KEY**

Your service **WILL NOT START** without `DJANGO_SECRET_KEY`. Follow these steps carefully:

**Step 1: Generate SECRET_KEY**

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output (it will be a long random string).

**Step 2: Add to Railway**

1. Go to Railway Dashboard → Your service → "Variables" tab
2. Click "New Variable"
3. **Variable Name**: `DJANGO_SECRET_KEY` (exactly as shown, case-sensitive)
   - ❌ **DO NOT** use: `SECRET_KEY`, `django_secret_key`, `DJANGO_SECRETKEY`
   - ✅ **USE**: `DJANGO_SECRET_KEY` (with underscores, all uppercase)
4. **Variable Value**: Paste the generated SECRET_KEY
5. Click "Add" or "Save"
6. **Verify**: The variable should appear in the list

**Step 3: Wait for Auto-Redeploy**

- Railway automatically redeploys when you add variables
- Wait 1-2 minutes
- Check "Deployments" tab for new deployment

**Step 4: Check Logs**

- Go to "Logs" tab
- Should see successful startup (no more `DJANGO_SECRET_KEY` errors)

**Common Mistakes**:
- ❌ Wrong name: `SECRET_KEY` → Use `DJANGO_SECRET_KEY`
- ❌ Wrong case: `django_secret_key` → Use `DJANGO_SECRET_KEY`
- ❌ Empty value → Make sure you paste the generated key
- ❌ Not saved → Click "Add" or "Save" after entering

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

#### Storage Configuration (FREE - No AWS Required!)

**Important**: You DON'T need AWS S3! Railway provides FREE local storage.

```
USE_S3=False
```

**This means**:
- ✅ Media files stored on Railway (FREE)
- ✅ No AWS account needed
- ✅ No additional cost
- ✅ Automatic setup

**Storage Options**:

**Option 1: Railway Local Storage (FREE) - Recommended**
- Files stored on Railway's container filesystem
- **FREE** - No additional cost
- Files persist as long as service is running
- Perfect for small to medium applications
- **Setup**: Nothing to do! Already configured with `USE_S3=False`

**Option 2: Railway Volumes (Persistent Storage) - Optional**
- Persistent storage that survives deployments
- **FREE** for small volumes (within Railway's free tier)
- **Setup**:
  1. Go to Railway Dashboard → Your service → "Settings" → "Volumes"
  2. Create a new volume (e.g., `media-storage`)
  3. Mount it to `/app/media`

**What Files Are Stored?**:
- Profile photos
- Company logos
- Bug report screenshots
- Generated PDFs (optional, can be regenerated)

**Storage Location**: `/app/media` on Railway container

**Note**: Remove AWS variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.) from Railway if they exist - they're not needed since `USE_S3=False`.

#### Optional

```
JOBS_FEATURE_ENABLED=False
DJANGO_LOG_LEVEL=INFO
CSRF_TRUSTED_ORIGINS=https://*.railway.app
```

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

**Recommended: Use Environment Variables** (Easiest - No Terminal Needed!) ⭐:

1. **Go to Railway Dashboard**
2. **Click on your Django app service**
3. **Go to "Variables" tab**
4. **Add 3 environment variables**:
   - `DJANGO_SUPERUSER_USERNAME` = `admin` (or your desired username)
   - `DJANGO_SUPERUSER_EMAIL` = `admin@example.com` (or your email)
   - `DJANGO_SUPERUSER_PASSWORD` = `your-secure-password` (choose a strong password)
5. **Redeploy your service**:
   - Go to "Deployments" tab
   - Click "Redeploy" on the latest deployment
   - OR: Push a new commit to trigger automatic deployment
6. **Done!** Superuser will be created automatically during deployment!

**Note**: The Dockerfile has been configured to automatically create the superuser if the environment variables are set. No manual command needed!

**Alternative: Railway Web Terminal** (if available):

1. **Go to Railway Dashboard**
2. **Click on your Django app service**
3. **Open Web Terminal**:
   - Go to **"Deployments"** tab → Latest deployment → **"Terminal"** tab
   - OR: **"Settings"** → **"Console"**
4. **Run createsuperuser**:
   ```bash
   python manage.py createsuperuser
   ```
5. **Follow prompts**: Enter username, email, and password

**Note**: The custom management command `create_superuser_from_env` is automatically run during deployment if the environment variables are set. See Step 4 below for more details.

---

## Post-Deployment Checklist

### Step 0: Find Your App URL 🌐

**To access your deployed application, you need to find your Railway app URL:**

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Login to your account

2. **Select Your Project**
   - Click on your project name

3. **Click on Your Django App Service**
   - Click on your Django app service (not PostgreSQL, Redis, or Celery worker)
   - It's usually the main service with your repo name

4. **Find Your URL**
   - **Option A**: Look at the top of the service page for **"Domains"** section
   - **Option B**: Go to **"Settings"** tab → Scroll to **"Domains"** section
   - **Option C**: Look for a **"Generate Domain"** button if no domain exists yet

5. **Your URL Format**:
   ```
   https://your-service-name.up.railway.app
   ```
   Or:
   ```
   https://your-app-name-production.up.railway.app
   ```

6. **Click the URL** to open your app in a browser

**📝 Note**: If you don't see a domain, click **"Generate Domain"** button to create one.

**Example URL**: `https://ai-resume-builder-jk.up.railway.app`

---

### Step 1: Check Service Status & Logs

**In Railway Dashboard**:
1. Click "Logs" tab (top navigation)
2. Check for errors:
   - Look for `DJANGO_SECRET_KEY` error → **Go to Step 2**
   - Look for database connection errors → **Go to Step 3**
   - Look for any other red error messages

**What to Look For**:

**✅ Success**: Should see Django server starting
```
Starting server...
Booting worker with pid: ...
```

**❌ Error**: If you see:
```
ValueError: DJANGO_SECRET_KEY environment variable is not set!
```
→ **Add `DJANGO_SECRET_KEY` to Railway variables** (see Environment Variables section above)

**❌ Error**: If you see:
```
django.db.utils.OperationalError: could not connect to server
```
→ **Link PostgreSQL service** (see Step 3 below)

### Step 2: Link PostgreSQL Database

**If Database Connection Error Appears**:

1. Go to "Variables" tab
2. Click "Reference Variable" button
3. Select PostgreSQL service from dropdown
4. Select `DATABASE_URL` from variable list
5. Click "Add"
6. Wait for redeploy (automatic)

**Verify Database Connection**:
- After redeploy, check logs
- Should see: "Connected to database" or similar
- No database connection errors

### Step 3: Run Database Migrations

**Option A: Using Railway CLI (Recommended)**

```powershell
# Navigate to project directory
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"

# Login to Railway (if not already)
railway login

# Link to your project (if not already)
railway link

# Run migrations
railway run python manage.py migrate
```

**Expected Output**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, users, resumes, jobs, pages
Running migrations:
  Applying users.0001_initial... OK
  Applying resumes.0001_initial... OK
  ...
```

**Option B: Check if Migrations Ran Automatically**

1. Go to "Logs" tab
2. Look for: "Running migrations..." or "Applying migrations..."
3. If you see migration messages → Migrations already ran ✅
4. If no migration messages → Run migrations manually (Option A)

### Step 4: Create Superuser (Admin Account)

**Method 1: Automatic Creation via Environment Variables (Recommended) ⭐**

This method automatically creates a superuser during deployment - no terminal needed!

1. **Go to Railway Dashboard** → Your Django app service → "Variables" tab
2. **Add these three environment variables**:
   - **Name**: `DJANGO_SUPERUSER_USERNAME` → **Value**: `admin` (or your desired username)
   - **Name**: `DJANGO_SUPERUSER_EMAIL` → **Value**: `admin@example.com` (or your email)
   - **Name**: `DJANGO_SUPERUSER_PASSWORD` → **Value**: `your-secure-password-here` (choose a strong password)
3. **Redeploy** your service (or push a new commit to trigger auto-deploy)
4. **Done!** Superuser will be created automatically during deployment ✅

**Method 2: Using Railway CLI (Alternative)**

```powershell
# Make sure you're logged in and linked
railway login
railway link

# Create superuser
railway run python manage.py createsuperuser
```

**Follow the prompts**:
- **Username**: `admin` (or your preferred username)
- **Email**: `admin@example.com` (optional but recommended)
- **Password**: Enter a strong password (you'll be asked twice)

**Expected Output**:
```
Superuser created successfully.
```

**Note**: Method 1 (environment variables) is recommended as it's easier and doesn't require terminal access.

### Step 5: Expose Service (Get Public URL)

**In Railway Dashboard**:

1. Go to "Settings" tab
2. Scroll to "Networking" section
3. Click "Generate Domain" button
   - Railway will generate a free domain like: `ai-resume-builder-production.up.railway.app`
4. Copy the domain (you'll need this)

**Alternative: Add Custom Domain**

1. Go to "Settings" → "Networking"
2. Click "Custom Domain"
3. Add your domain (if you have one)
4. Update DNS records as instructed

### Step 6: Verify Everything Works

**Test Your App**:

1. Open your Railway domain in browser:
   - Example: `https://ai-resume-builder-production.up.railway.app`

2. Test Features:
   - [ ] Home page loads
   - [ ] User registration works
   - [ ] User login works
   - [ ] Resume builder works
   - [ ] PDF generation works
   - [ ] Admin dashboard accessible: `https://your-domain.railway.app/users/admin-login/`

**Check Service Status**:

1. Go to Railway Dashboard
2. Check service status:
   - Should be **"Running"** (green)
   - Should show **"1 Replica"** (or more)

### Quick Status Checklist

- [ ] **Step 1**: Checked logs - no `DJANGO_SECRET_KEY` error
- [ ] **Step 2**: Set `DJANGO_SECRET_KEY` in Railway variables
- [ ] **Step 3**: Linked PostgreSQL database (`DATABASE_URL`)
- [ ] **Step 4**: Ran database migrations
- [ ] **Step 5**: Created superuser (admin account)
- [ ] **Step 6**: Exposed service (got public URL)
- [ ] **Step 7**: Tested app - everything works
- [ ] **Step 8**: Set up Celery worker (optional, see Celery Worker Setup section)

---

## Celery Worker Setup

Your app uses Celery for async tasks like:
- PDF generation
- Resume parsing
- Resume scoring

### ✅ Celery is FREE on Railway!

**Important**: 
- Celery is **FREE** (open-source library)
- Redis is **FREE** (included in Railway free tier)
- Running Celery worker is **FREE** (uses Railway's $5/month free credit)
- **No additional payment required!** ✅

### Option 1: Separate Service (Recommended for Production) ✅

**In Railway Dashboard**:
1. Click on your project
2. Click "New" → "Empty Service"
3. Name it "celery-worker"
4. Connect to the same GitHub repository
5. Go to "Settings" → "Deploy"
6. Set "Start Command":
   ```
   celery -A core worker -l info --concurrency=4
   ```
   **Note**: Using `prefork` pool (default) - most stable with Redis, no monkey patching needed.
   **Alternative**: If you need higher concurrency, use `-P threads --concurrency=10` instead.

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
   worker: celery -A core worker -l info --concurrency=4
   ```
   **Note**: Using `prefork` pool (default) for stability. For higher concurrency, use `-P threads --concurrency=10`.

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

- **Pool Type**: Using `prefork` pool (default) - most stable with Redis, no monkey patching conflicts
- **Redis Connection**: Automatically configured via `REDIS_URL` from Railway
- **Task Serialization**: Uses JSON (already configured)
- **Concurrency**: Set to 4 workers by default (adjust based on your needs)
- **Alternative**: For higher concurrency, use `-P threads --concurrency=10` in start command

---

## Troubleshooting

### GitHub Connection Stuck on "Loading..."

**Symptoms**:
- Railway page shows "Loading..." indefinitely
- Can't see your GitHub repositories
- "Configure GitHub App" button visible but not working

**Solutions**:

1. **Click "Configure GitHub App" Button**:
   - Click the gear icon or "Configure GitHub App" button
   - This will redirect you to GitHub authorization page
   - Authorize Railway to access your repositories
   - Grant necessary permissions

2. **Manually Authorize GitHub**:
   - Go to: https://github.com/settings/installations
   - Find "Railway" in the list
   - Click "Configure"
   - Grant access to repositories (or all repositories)
   - Save changes

3. **Refresh Railway Page**:
   - Go back to Railway
   - Refresh the page (F5 or Ctrl+R)
   - Try selecting repository again

4. **Use Alternative Method**:
   - If GitHub connection doesn't work, use CLI method (Option 2)
   - Or deploy from a template and connect GitHub later

5. **Clear Browser Cache**:
   - Clear browser cache and cookies
   - Try in incognito/private window
   - Or try a different browser

### Application Won't Start - DJANGO_SECRET_KEY Error

**Error**: `ValueError: DJANGO_SECRET_KEY environment variable is not set!`

**Fix**:
1. Go to Railway Dashboard → Your service → "Variables" tab
2. Check if `DJANGO_SECRET_KEY` exists:
   - If **NOT** in the list → Click "New Variable"
   - If **exists** but wrong → Click edit icon (pencil)
3. **Add/Update Variable**:
   - **Name**: `DJANGO_SECRET_KEY` (exactly, case-sensitive)
   - **Value**: Generate using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Click "Add" or "Save"
4. **Wait for Auto-Redeploy**: Railway automatically redeploys when you add variables
5. **Check Logs**: Should see successful startup (no more errors)

**Common Mistakes**:
- ❌ Wrong name: `SECRET_KEY` → Use `DJANGO_SECRET_KEY`
- ❌ Wrong case: `django_secret_key` → Use `DJANGO_SECRET_KEY`
- ❌ Empty value → Make sure you paste the generated key
- ❌ Not saved → Click "Add" or "Save" after entering

### Bad Request (400) Error - ALLOWED_HOSTS Issue

**Error**: `Bad Request (400)` when accessing your Railway app URL

**Root Cause**: Django's `ALLOWED_HOSTS` setting doesn't include your Railway domain.

**Solution**: The code automatically sets Railway domains when `ALLOWED_HOSTS` is empty. However, if you still get this error:

1. **Set Environment Variables Manually**:
   - Go to Railway Dashboard → Your Django app service → "Variables" tab
   - Add/Update:
     - **Name**: `ALLOWED_HOSTS`
     - **Value**: `ai-resume-builder-jk.up.railway.app` (your Railway domain)
     - **Name**: `CSRF_TRUSTED_ORIGINS`
     - **Value**: `https://ai-resume-builder-jk.up.railway.app`
2. **Redeploy** the service
3. **Verify**: Your app should load correctly at your Railway URL

**Note**: The automatic fix in code should handle this, but setting it manually ensures it works immediately.

### DNS Error: "This site can't be reached" / DNS_PROBE_FINISHED_NXDOMAIN

**Symptoms**:
- Browser shows "This site can't be reached"
- Error code: `DNS_PROBE_FINISHED_NXDOMAIN`
- Domain doesn't resolve

**Solutions**:

1. **Check Service Status**:
   - Go to Railway Dashboard → Your Django service
   - Verify status is **"Running"** (green)
   - If paused/stopped, click **"Start"** or **"Redeploy"**

2. **Verify Domain**:
   - Go to **Settings** tab → **Networking** section
   - Check if domain exists: `https://your-service-name.up.railway.app`
   - If no domain, click **"Generate Domain"** button
   - **Important**: Use the domain shown in Railway, not an old one

3. **Restart Service**:
   - Go to **Deployments** tab
   - Click **"Redeploy"** on latest deployment
   - Wait 2-3 minutes for redeploy

4. **Check Logs**:
   - Go to **Logs** tab
   - Look for startup errors or crashes
   - If service crashed, check error messages

5. **Verify Service is Active**:
   - Railway Dashboard → Your service
   - Should show **"1 Replica"** or more
   - Should show **"Running"** status

**Common Causes**:
- Service was paused/stopped (free tier services pause after inactivity)
- Domain changed (Railway sometimes regenerates domains)
- Service crashed and needs restart
- Deployment failed

### Application Won't Start - Other Errors

**Check Logs**:
1. In Railway Dashboard → Your service → "Deployments" → "View Logs"
2. Look for errors

**Common Issues**:
- Missing environment variables → Add them in "Variables" tab
- Database connection errors → Link PostgreSQL service
- Migration errors → Run migrations manually
- ALLOWED_HOSTS errors → See "Bad Request (400) Error" section above

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
   - Should be: `celery -A core worker -l info --concurrency=4`
   - Verify in "Settings" → "Deploy"
   - **Alternative**: For higher concurrency: `celery -A core worker -l info -P threads --concurrency=10`

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
- Wrong start command: Use `celery -A core worker -l info --concurrency=4` (prefork pool, default)
- Worker crashes with eventlet errors: Use prefork pool (default) instead of eventlet for stability
- Worker service not created: Create separate service for worker

---

## Cost Estimation

### Railway Free Tier

**How Railway Credits Work**:
1. **Sign-up Bonus**: Railway gives you **$5 one-time credit** when you first sign up (30-day trial)
2. **Monthly Free Credit**: After trial, Railway gives you **$1/month free credit** (doesn't roll over)
3. **PostgreSQL**: **FREE** (included, doesn't use credit)
4. **Redis**: **FREE** (included, doesn't use credit)

**Who Provides the Credit?**
- ✅ **Railway.app provides it** - It's their free tier offering
- ✅ **No payment method required** - You get it automatically
- ✅ **No cost to you** - Railway gives it for free
- ✅ **Renews monthly** - $1 credit every month (after initial $5)

### Estimated Monthly Cost: **$0** (Free Tier)

**Configuration**:
- Web service (Django app): ~$0.50-1/month (within $1/month credit)
- PostgreSQL: **FREE** (included, no charge, doesn't use credit)
- Redis: **FREE** (included, no charge, doesn't use credit)
- Celery worker: ~$0.50-1/month (within $1/month credit)
- **Total usage**: ~$1-2/month → **FREE** (within $1/month credit + initial $5)

**Total**: **$0/month** if you stay within free tier limits!

**Note**: 
- Small apps (like yours) typically use ~$0.50-1/month
- Railway's $1/month free credit is usually enough
- If you exceed $1/month, you'd need to add payment method (but small apps rarely do)

### ✅ Celery is FREE on Railway!

**Important Points**:
- ✅ **Celery is FREE** - It's an open-source Python library (no cost)
- ✅ **Redis is FREE** - Railway includes Redis in free tier
- ✅ **Worker service is FREE** - Runs on Railway's free credit
- ✅ **No additional payment** - Everything runs on Railway's free credit ($1/month + initial $5)

**Why it's free**:
- Celery is just Python code running as a background process
- Railway charges based on resource usage (CPU, RAM, time)
- A small Celery worker uses minimal resources (~$0.50-1/month)
- Stays well within the $1/month free credit

**What uses Railway credit**:
- Web service (Django app) - ~$0.50-1/month
- Celery worker service - ~$0.50-1/month
- PostgreSQL - **FREE** (included, doesn't use credit)
- Redis - **FREE** (included, doesn't use credit)

**Total**: ~$1-2/month → **FREE** (within $1/month credit + initial $5 bonus) ✅

**Railway Credit Breakdown**:
- **Initial**: $5 one-time credit (when you sign up)
- **Monthly**: $1 free credit (every month, doesn't roll over)
- **Your usage**: ~$1/month (small Django app + Celery worker)
- **Result**: **FREE** ✅ (stays within $1/month free credit)

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
- ✅ Free PostgreSQL included (doesn't use credit)
- ✅ Free Redis included (doesn't use credit)
- ✅ $1/month free credit + $5 initial bonus (enough for small apps)
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ Simple setup

**How Railway Credits Work**:
- **Railway gives you**: $5 one-time credit when you sign up
- **Railway gives you**: $1 free credit every month (after trial)
- **You don't pay**: Railway provides these credits for free
- **No payment method needed**: For free tier usage

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

