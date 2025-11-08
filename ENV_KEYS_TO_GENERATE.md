# Environment Variables - What Keys to Generate

## 🎯 Quick Answer

You need to generate/prepare these environment variable keys:

### 1. ✅ DJANGO_SECRET_KEY (Generate Now)
**Status**: ⚠️ **MUST GENERATE**

Generate using:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example Output**:
```
%w)2qxuhyre46!)j7-b6tp#7d@thhw3+y)iuu%w)8mvwh=zi)r
```

**Save this value** - You'll need it for:
- Development: `.env` file
- Production: Fly.io secrets

---

### 2. ✅ GOOGLE_AI_API_KEY (Get from Google)
**Status**: ⚠️ **MUST GET**

**Steps**:
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key
5. Save it securely

**Example**:
```
AIzaSyAbc123def456ghi789jkl012mno345pqr
```

---

### 3. ✅ Database Credentials (From Fly.io)
**Status**: ⏳ **GET DURING DEPLOYMENT**

These are automatically provided by Fly.io when you create a Postgres database:
- `DB_NAME` - Auto-generated
- `DB_USER` - Auto-generated  
- `DB_PASSWORD` - Auto-generated
- `DB_HOST` - Auto-generated
- `DB_PORT` - Usually `5432`

**You don't need to generate these** - Fly.io provides them.

---

### 4. ✅ Redis Credentials (From Fly.io)
**Status**: ⏳ **GET DURING DEPLOYMENT**

These are automatically provided by Fly.io when you create Redis:
- `CELERY_BROKER_URL` - Auto-generated
- `CELERY_RESULT_BACKEND` - Auto-generated

**You don't need to generate these** - Fly.io provides them.

---

## 📋 Complete List

### Must Generate/Get Now (Before Deployment)

| Variable | How to Get | Status |
|----------|------------|--------|
| `DJANGO_SECRET_KEY` | Generate using Python command | ⚠️ **DO NOW** |
| `GOOGLE_AI_API_KEY` | Get from Google AI Studio | ⚠️ **DO NOW** |

### Get During Deployment (From Fly.io)

| Variable | How to Get | Status |
|----------|------------|--------|
| `DB_NAME` | Auto-set by Fly Postgres | ⏳ During deployment |
| `DB_USER` | Auto-set by Fly Postgres | ⏳ During deployment |
| `DB_PASSWORD` | Auto-set by Fly Postgres | ⏳ During deployment |
| `DB_HOST` | Auto-set by Fly Postgres | ⏳ During deployment |
| `DB_PORT` | Auto-set by Fly Postgres | ⏳ During deployment |
| `CELERY_BROKER_URL` | Auto-set by Fly Redis | ⏳ During deployment |
| `CELERY_RESULT_BACKEND` | Auto-set by Fly Redis | ⏳ During deployment |

### Set Values (No Generation Needed)

| Variable | Value | Status |
|----------|-------|--------|
| `DEBUG` | `False` (production) | ✅ Just set value |
| `ALLOWED_HOSTS` | `yourapp.fly.dev` | ✅ Just set value |
| `USE_POSTGRESQL` | `True` (production) | ✅ Just set value |
| `USE_GEMINI` | `True` | ✅ Just set value |
| `JOBS_FEATURE_ENABLED` | `False` | ✅ Just set value |
| `DJANGO_LOG_LEVEL` | `INFO` | ✅ Just set value |

---

## 🚀 Action Plan

### Step 1: Generate SECRET_KEY (2 minutes)

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** and save it somewhere safe.

**Example** (yours will be different):
```
%w)2qxuhyre46!)j7-b6tp#7d@thhw3+y)iuu%w)8mvwh=zi)r
```

---

### Step 2: Get GOOGLE_AI_API_KEY (5 minutes)

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in
3. Click "Create API Key"
4. Copy the key
5. Save it securely

---

### Step 3: Create .env File (5 minutes)

Create a `.env` file in your project root:

```env
# Critical - Required
DJANGO_SECRET_KEY=%w)2qxuhyre46!)j7-b6tp#7d@thhw3+y)iuu%w)8mvwh=zi)r
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google AI
GOOGLE_AI_API_KEY=your-google-ai-api-key-here

# Database (Development - SQLite)
USE_POSTGRESQL=False

# Celery (Development - Local Redis)
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Optional
USE_GEMINI=True
JOBS_FEATURE_ENABLED=False
DJANGO_LOG_LEVEL=INFO
```

**Replace**:
- `%w)2qxuhyre46!)j7-b6tp#7d@thhw3+y)iuu%w)8mvwh=zi)r` with your generated SECRET_KEY
- `your-google-ai-api-key-here` with your actual Google AI API key

---

## ✅ Checklist

### Before Deployment:
- [ ] **DJANGO_SECRET_KEY** - Generated and saved
- [ ] **GOOGLE_AI_API_KEY** - Obtained from Google and saved
- [ ] **.env file** - Created with all values

### During Deployment:
- [ ] **Database credentials** - Will be auto-set by Fly.io
- [ ] **Redis credentials** - Will be auto-set by Fly.io
- [ ] **Fly.io secrets** - Set using `fly secrets set`

---

## 🔐 Security Notes

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Never share SECRET_KEY** - Keep it secret
3. **Never commit API keys** - Keep them in `.env` or Fly.io secrets
4. **Generate new SECRET_KEY for production** - Don't reuse development key

---

## 📝 Summary

**What you need to generate NOW**:
1. ✅ `DJANGO_SECRET_KEY` - Generate using Python command
2. ✅ `GOOGLE_AI_API_KEY` - Get from Google AI Studio

**What you'll get during deployment**:
- Database credentials (from Fly Postgres)
- Redis credentials (from Fly Redis)

**What you just set**:
- `DEBUG=False`
- `ALLOWED_HOSTS=yourapp.fly.dev`
- Other configuration values

---

## 🎯 Next Steps

1. ✅ Generate SECRET_KEY (command above)
2. ✅ Get GOOGLE_AI_API_KEY (from Google)
3. ✅ Create `.env` file with these values
4. ⏳ Continue with deployment (database/Redis will be auto-set)

---

**For complete details, see**: `ENV_VARIABLES_GUIDE.md`

