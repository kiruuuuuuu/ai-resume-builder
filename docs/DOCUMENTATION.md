# AI Resume Builder - Complete Documentation

This document consolidates all setup, configuration, and deployment guides for the AI Resume Builder project.

---

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Celery Configuration](#celery-configuration)
3. [Deployment Guide](#deployment-guide)
4. [Social Login Setup](#social-login-setup)
5. [Database Configuration](#database-configuration)
6. [Environment Variables](#environment-variables)

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Redis (for Celery background tasks)
- PostgreSQL (for production) or SQLite (for development)
- Google AI API Key (for Gemini features)

### Method 1: Recommended Setup (with Conda)

This method is highly recommended as it simplifies the installation of WeasyPrint and its dependencies, which are required for generating PDF resumes.

1. **Install Miniconda**: Download and install from [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

2. **Create and Activate Conda Environment**:
   ```bash
   # Create a new environment named 'resume_env' with Python 3.11
   conda create -n resume_env python=3.11 -y
   
   # Activate the environment
   conda activate resume_env
   ```

3. **Install WeasyPrint**:
   ```bash
   # Install WeasyPrint and its native dependencies from the conda-forge channel
   conda install -c conda-forge weasyprint -y
   ```

4. **Install Python Dependencies & Set Up Database**:
   ```bash
   # Navigate to your project directory
   cd path/to/your/AI_Resume_Builder
   
   # Install all required packages
   pip install -r requirements.txt
   
   # Create the database schema
   python manage.py migrate
   ```

### Method 2: Alternative Setup (with venv)

Use this method if you prefer not to use Conda. Note that PDF generation may fail unless you manually install the required GTK dependencies for WeasyPrint.

1. **Create and Activate Virtual Environment**:
   ```bash
   # Navigate to your project directory
   cd path/to/your/AI_Resume_Builder
   
   # Create a virtual environment named 'resume_env'
   python -m venv resume_env
   
   # Activate the environment
   # Windows:
   .\resume_env\Scripts\Activate.ps1
   # Linux/Mac:
   source resume_env/bin/activate
   ```

2. **Install Dependencies & Set Up Database**:
   ```bash
   # Install all required packages
   pip install -r requirements.txt
   
   # Create the database schema
   python manage.py migrate
   ```

### Environment Configuration

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your configuration:
   - Set `DJANGO_SECRET_KEY` (generate one: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
   - Set `GOOGLE_AI_API_KEY` (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - Configure database settings (see [Database Configuration](#database-configuration))
   - Set `DEBUG=True` for development

### Running the Application

After completing either setup method, you need to run three services in three separate terminals.

**Terminal 1: Start the Redis Server**

Redis is our message broker for background tasks.

- **Windows**: Download and extract Redis from [Redis for Windows](https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip)
- **Linux/Mac**: Install via package manager: `sudo apt-get install redis-server` or `brew install redis`

```bash
# Navigate to Redis directory (Windows) or use system service (Linux/Mac)
cd C:\Redis-x64-3.0.504
.\redis-server.exe

# Linux/Mac (if installed as service):
sudo systemctl start redis
# Or run directly:
redis-server
```

Leave this terminal running.

**Terminal 2: Start the Celery Worker**

This worker process handles the background AI tasks.

```bash
# Activate your environment
conda activate resume_env  # or: source resume_env/bin/activate

# Navigate to project directory
cd path/to/your/AI_Resume_Builder

# For Windows (Development):
celery -A core worker -l info -P solo

# For Linux/Mac (Production):
celery -A core worker -l info -P eventlet --concurrency=50
```

**Terminal 3: Start the Django Server**

```bash
# Activate your environment
conda activate resume_env  # or: source resume_env/bin/activate

# Navigate to project directory
cd path/to/your/AI_Resume_Builder

# Start the server
python manage.py runserver
```

### Access the Application

With all three terminals running, you can access the AI Resume Builder in your web browser at:

**http://127.0.0.1:8000/**

---

## Celery Configuration

### Understanding Your Tasks

Your AI Resume Builder uses **I/O-bound tasks**:
- `parse_resume_task` - Waits for file I/O and Gemini API responses
- `update_resume_score_task` - Waits for Gemini API responses  
- `calculate_and_save_match_score_task` - Waits for Gemini API responses

These tasks spend **most of their time waiting** for external services (API calls, file operations), not computing.

### Eventlet Pool (`-P eventlet`)

#### How It Works:
- Uses **green threads** (coroutines) - lightweight threads managed by eventlet
- Implements **cooperative multitasking** - tasks yield control when waiting
- **Monkey patches** Python's standard library to make I/O operations non-blocking
- Multiple tasks can run "concurrently" in a single OS thread

#### Key Features:
```python
# With eventlet, this happens:
Task 1: Calls Gemini API → yields control (waits)
Task 2: Calls Gemini API → yields control (waits)  
Task 3: Processes file → yields control (waits)
# While waiting, eventlet switches between tasks
# When API responds, task resumes execution
```

#### Benefits:
✅ **Handles multiple tasks simultaneously** (many resumes can be processed "at once")
✅ **Efficient for I/O-bound tasks** - no wasted time while waiting
✅ **Low memory overhead** - green threads are lightweight
✅ **Can handle hundreds of concurrent tasks** in one worker process

#### Limitations:
❌ **Windows Compatibility Issues** - blocking I/O from mainloop causes errors
❌ **Requires monkey patching** - modifies standard library behavior
❌ **Not ideal for CPU-bound tasks** - tasks must cooperate (yield control)
❌ **Can be complex to debug** - async behavior can be tricky

#### Example:
```bash
# Can process 50 resumes "concurrently"
# While waiting for API #1, it processes API #2, #3, #4...
celery -A core worker -l info -P eventlet --concurrency=50
```

### Solo Pool (`-P solo`)

#### How It Works:
- **Single-threaded** - processes tasks one at a time
- **Sequential execution** - no concurrency or multitasking
- **Simple and predictable** - easy to understand and debug

#### Benefits:
✅ **Windows Compatible** - no blocking I/O issues
✅ **Simple to debug** - straightforward execution flow
✅ **No additional dependencies** - works out of the box
✅ **Reliable** - no race conditions or async complexity

#### Limitations:
❌ **No concurrent processing** - tasks execute one after another
❌ **Slower for multiple requests** - must wait for each task to complete
❌ **Not production-optimized** - inefficient for high-traffic scenarios

#### Example:
```bash
# Processes tasks one at a time
# Task 2 waits for Task 1 to finish completely
celery -A core worker -l info -P solo
```

### Platform Recommendations

#### Windows (Development)
**Recommended**: Use `solo` pool
```bash
celery -A core worker -l info -P solo
```

**Why**: Avoids eventlet blocking I/O issues on Windows. Simple, reliable, and sufficient for development.

#### Linux/Mac (Production)
**Recommended**: Use `eventlet` pool
```bash
celery -A core worker -l info -P eventlet --concurrency=50
```

**Why**: Handles multiple I/O-bound tasks efficiently. Can process 50-100+ tasks simultaneously, providing better user experience and faster response times.

**Installation**:
```bash
pip install eventlet
```

---

## Deployment Guide

### Platform-Specific Celery Setup

This project is configured to work optimally on both Windows (development) and Linux/Mac (production).

### For Windows Development

#### Configuration:
- **Pool Type**: `solo` (single-threaded)
- **Command**: `celery -A core worker -l info -P solo`
- **Why**: Avoids eventlet blocking I/O issues on Windows
- **Performance**: Processes tasks sequentially (one at a time)

#### Pros:
✅ Reliable, no runtime errors
✅ Simple debugging
✅ No additional dependencies needed

#### Cons:
❌ No concurrent task processing
❌ Slower for multiple simultaneous requests

### For Linux/Mac Production

#### Configuration:
- **Pool Type**: `eventlet` (green threads, concurrent)
- **Command**: `celery -A core worker -l info -P eventlet --concurrency=50`
- **Why**: Handles multiple I/O-bound tasks efficiently
- **Performance**: Can process 50-100+ tasks simultaneously

#### Installation:
```bash
# Make sure eventlet is installed
pip install eventlet
```

#### Pros:
✅ High concurrency (50-100+ tasks)
✅ Efficient for I/O-bound operations (API calls)
✅ Better user experience (faster response times)
✅ Production-ready performance

#### Cons:
⚠️ Requires eventlet package
⚠️ More complex (but handled automatically by the code)

### Production Deployment Checklist

1. **Environment Variables**:
   - Set `DEBUG=False`
   - Set `ALLOWED_HOSTS` to your domain(s)
   - Configure `SECRET_KEY` (never commit this!)
   - Set up PostgreSQL database
   - Configure Redis for Celery

2. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```
   The project uses WhiteNoise for serving static files in production.

3. **Database Migration**:
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Services**:
   - Start Redis server
   - Start Celery worker (with eventlet pool)
   - Start Django application (using gunicorn or uwsgi)

### Example Production Setup (Linux)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv redis-server postgresql postgresql-contrib

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn eventlet

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Setup database
sudo -u postgres createdb ai_resume_builder
python manage.py migrate
python manage.py collectstatic

# Start services (using systemd or supervisor)
# See your deployment platform's documentation for process management
```

---

## Social Login Setup

This project uses **django-allauth** for OAuth authentication. The buttons are now configured and ready to work, but you need to set up OAuth credentials from Google and GitHub.

### Current Status

✅ **Code is configured** - All URLs and settings are ready  
⚠️ **OAuth credentials needed** - You need to get Client IDs and Secrets  
⚠️ **Database migration needed** - Run migrations after installing django-allauth  

### Setup Steps

#### 1. Install Dependencies

```bash
pip install django-allauth cryptography
```

**Note**: `cryptography` is required by django-allauth for OAuth providers like Google.

#### 2. Run Migrations

```bash
python manage.py migrate
```

This will create the necessary tables for django-allauth.

#### 3. Create a Site in Django Admin

```bash
python manage.py createsuperuser  # If you don't have one
python manage.py runserver
```

Then:
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to **Sites** → **Sites**
3. Edit the default site (usually "example.com")
4. Set **Domain name** to: `127.0.0.1:8000` (for development) or your production domain
5. Set **Display name** to: `AI Resume Builder` or your site name
6. Save

#### 4. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google+ API** (or use Google Identity Services)
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Web application**
6. Add authorized redirect URIs:
   - **Development**: `http://127.0.0.1:8000/accounts/google/login/callback/`
     - ✅ Add this for local testing
   - **Production**: `https://yourdomain.com/accounts/google/login/callback/`
     - ⚠️ Replace `yourdomain.com` with your actual domain (e.g., `myresumebuilder.com`)
     - ⚠️ Must use `https://` (not `http://`) for production
     - ⚠️ Add this when you deploy your application
   - **Note**: You can add both URIs to the same OAuth client - Google will use the appropriate one based on where the request comes from
7. Copy the **Client ID** and **Client Secret**

#### 5. Get GitHub OAuth Credentials

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: AI Resume Builder
   - **Homepage URL**: `http://127.0.0.1:8000` (development) or your production URL
   - **Authorization callback URL**: `http://127.0.0.1:8000/accounts/github/login/callback/` (development) or production callback URL
4. Click **Register application**
5. Copy the **Client ID** and generate a **Client Secret**

#### 6. Configure Environment Variables

Add to your `.env` file:

```bash
# Google OAuth (optional - uncomment if using)
# SOCIALACCOUNT_PROVIDERS_GOOGLE_CLIENT_ID=your-google-client-id
# SOCIALACCOUNT_PROVIDERS_GOOGLE_SECRET=your-google-client-secret

# GitHub OAuth (optional - uncomment if using)
# SOCIALACCOUNT_PROVIDERS_GITHUB_CLIENT_ID=your-github-client-id
# SOCIALACCOUNT_PROVIDERS_GITHUB_SECRET=your-github-client-secret
```

#### 7. Update Django Settings (if needed)

The settings are already configured in `core/settings.py`. If you need to customize:

```python
# In core/settings.py (already configured)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('SOCIALACCOUNT_PROVIDERS_GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('SOCIALACCOUNT_PROVIDERS_GOOGLE_SECRET', ''),
            'key': ''
        }
    },
    'github': {
        'APP': {
            'client_id': os.getenv('SOCIALACCOUNT_PROVIDERS_GITHUB_CLIENT_ID', ''),
            'secret': os.getenv('SOCIALACCOUNT_PROVIDERS_GITHUB_SECRET', ''),
            'key': ''
        }
    }
}
```

### Testing Social Login

1. Start your Django server
2. Navigate to the login/register page
3. Click the "Google" or "GitHub" button
4. You should be redirected to the OAuth provider's login page
5. After authorization, you'll be redirected back and logged in

### Troubleshooting

- **"Site matching query does not exist"**: Make sure you've created/updated the Site in Django admin (step 3)
- **"Redirect URI mismatch"**: Verify the redirect URI in your OAuth app settings matches exactly
- **"Invalid credentials"**: Double-check your Client ID and Secret in the `.env` file

---

## Database Configuration

### Development (SQLite)

By default, the project uses SQLite for development. No additional configuration is needed.

```bash
# In .env file
USE_POSTGRESQL=False
```

### Production (PostgreSQL)

For production deployments, use PostgreSQL for better performance and scalability.

#### 1. Install PostgreSQL

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Windows**: Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

#### 2. Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE ai_resume_builder;

# Create user
CREATE USER ai_resume_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_resume_builder TO ai_resume_user;

# Exit
\q
```

#### 3. Configure Environment Variables

Add to your `.env` file:

```bash
USE_POSTGRESQL=True
DB_NAME=ai_resume_builder
DB_USER=ai_resume_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

#### 4. Install PostgreSQL Driver

The `psycopg2-binary` package is already in `requirements.txt`. If you need to install it separately:

```bash
pip install psycopg2-binary
```

#### 5. Run Migrations

```bash
python manage.py migrate
```

### Database Backup and Restore

**Backup**:
```bash
pg_dump -U ai_resume_user ai_resume_builder > backup.sql
```

**Restore**:
```bash
psql -U ai_resume_user ai_resume_builder < backup.sql
```

---

## Environment Variables

All environment variables should be set in a `.env` file in the project root. See `.env.example` for a complete template.

### Required Variables

- `DJANGO_SECRET_KEY` - Django secret key (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- `GOOGLE_AI_API_KEY` - Google AI API key for Gemini features

### Optional Variables

- `DEBUG` - Set to `True` for development, `False` for production (default: `True`)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `USE_POSTGRESQL` - Set to `True` to use PostgreSQL (default: `False`)
- `USE_S3` - Set to `True` to use AWS S3 for media storage (default: `False`)
- `USE_GEMINI` - Enable/disable Gemini features (default: `True`)

See `.env.example` for the complete list of available environment variables.

---

## Troubleshooting

### Common Issues

1. **WeasyPrint PDF Generation Fails**:
   - Use Conda installation method (recommended)
   - Or manually install GTK dependencies for your platform

2. **Celery Worker Not Processing Tasks**:
   - Ensure Redis is running
   - Check Celery worker logs for errors
   - Verify `CELERY_BROKER_URL` in settings

3. **Database Connection Errors**:
   - Verify database credentials in `.env`
   - Ensure PostgreSQL service is running (if using PostgreSQL)
   - Check database user permissions

4. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Verify WhiteNoise is configured correctly

5. **Social Login Not Working**:
   - Verify OAuth credentials in `.env`
   - Check Site configuration in Django admin
   - Verify redirect URIs match exactly

---

## Support

For issues or questions, please check the project's README or open an issue on the repository.

---

**Last Updated**: 2025

