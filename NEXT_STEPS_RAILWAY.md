# Next Steps After Successful Railway Deployment

## ✅ Current Status

- ✅ **Deployment Successful**: Your code is deployed
- ⚠️ **Service Status**: "Unexposed service" (not publicly accessible yet)
- ⚠️ **Environment Variables**: Need to verify `DJANGO_SECRET_KEY` is set

---

## 🔍 Step 1: Check Service Status & Logs

### In Railway Dashboard:

1. **Click "Logs" tab** (top navigation, next to "Deployments")
2. **Check for errors**:
   - Look for `DJANGO_SECRET_KEY` error
   - Look for database connection errors
   - Look for any other red error messages

### What to Look For:

**✅ Success**: Should see Django server starting
```
Starting server...
Booting worker with pid: ...
```

**❌ Error**: If you see:
```
ValueError: DJANGO_SECRET_KEY environment variable is not set!
```
→ **Go to Step 2** (Set Environment Variables)

**❌ Error**: If you see:
```
django.db.utils.OperationalError: could not connect to server
```
→ **Go to Step 3** (Link PostgreSQL)

---

## 🔑 Step 2: Set Environment Variables (CRITICAL)

### If `DJANGO_SECRET_KEY` Error Appears:

1. **Go to "Variables" tab** in Railway Dashboard
2. **Check if `DJANGO_SECRET_KEY` exists**:
   - If **NOT** in the list → Click "New Variable"
   - If **exists** but wrong → Click edit icon (pencil)

3. **Add/Update Variable**:
   - **Name**: `DJANGO_SECRET_KEY` (exactly, case-sensitive)
   - **Value**: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`
   - Click "Add" or "Save"

4. **Add Other Required Variables** (if not already set):
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `*.railway.app`
   - `GOOGLE_AI_API_KEY` = `your-google-ai-api-key`
   - `USE_GEMINI` = `True`
   - `USE_S3` = `False`

5. **Wait for Auto-Redeploy**:
   - Railway automatically redeploys when you add/update variables
   - Wait 1-2 minutes
   - Check "Deployments" tab for new deployment

---

## 🗄️ Step 3: Link PostgreSQL Database

### If Database Connection Error Appears:

1. **Go to "Variables" tab**
2. **Click "Reference Variable"** button
3. **Select PostgreSQL service** from dropdown
4. **Select `DATABASE_URL`** from variable list
5. **Click "Add"**
6. **Wait for redeploy** (automatic)

### Verify Database Connection:

After redeploy, check logs:
- Should see: "Connected to database" or similar
- No database connection errors

---

## 🗃️ Step 4: Run Database Migrations

### Option A: Using Railway CLI (Recommended)

**Open PowerShell**:

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

### Option B: Check if Migrations Ran Automatically

1. **Go to "Logs" tab**
2. **Look for**: "Running migrations..." or "Applying migrations..."
3. **If you see migration messages** → Migrations already ran ✅
4. **If no migration messages** → Run migrations manually (Option A)

---

## 👤 Step 5: Create Superuser (Admin Account)

### Using Railway CLI:

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

---

## 🌐 Step 6: Expose Service (Get Public URL)

### In Railway Dashboard:

1. **Go to "Settings" tab**
2. **Scroll to "Networking" section**
3. **Click "Generate Domain"** button
   - Railway will generate a free domain like: `ai-resume-builder-production.up.railway.app`
4. **Copy the domain** (you'll need this)

### Alternative: Add Custom Domain

1. **Go to "Settings" → "Networking"**
2. **Click "Custom Domain"**
3. **Add your domain** (if you have one)
4. **Update DNS records** as instructed

---

## ✅ Step 7: Verify Everything Works

### Test Your App:

1. **Open your Railway domain** in browser:
   - Example: `https://ai-resume-builder-production.up.railway.app`

2. **Test Features**:
   - [ ] Home page loads
   - [ ] User registration works
   - [ ] User login works
   - [ ] Resume builder works
   - [ ] PDF generation works
   - [ ] Admin dashboard accessible: `https://your-domain.railway.app/users/admin-login/`

### Check Service Status:

1. **Go to Railway Dashboard**
2. **Check service status**:
   - Should be **"Running"** (green)
   - Should show **"1 Replica"** (or more)

---

## 🔧 Step 8: Set Up Celery Worker (Optional but Recommended)

**Why**: Celery handles async tasks like PDF generation.

### In Railway Dashboard:

1. **Click "New" → "Empty Service"**
2. **Name it**: `celery-worker`
3. **Connect to GitHub** (same repository)
4. **Go to "Settings" → "Deploy"**
5. **Set "Start Command**:
   ```
   celery -A core worker -l info -P eventlet --concurrency=10
   ```

6. **Add Environment Variables**:
   - Go to "Variables" tab
   - **Reference Variables** from main service:
     - `DATABASE_URL` (from PostgreSQL service)
     - `REDIS_URL` (from Redis service)
   - **Add Same Variables** as main service:
     - `DJANGO_SECRET_KEY`
     - `DEBUG=False`
     - `ALLOWED_HOSTS=*.railway.app`
     - `GOOGLE_AI_API_KEY`
     - `USE_GEMINI=True`
     - `USE_S3=False`

7. **Verify Worker is Running**:
   - Go to "Logs" tab
   - Should see: `celery@v1 ready.`

---

## 📊 Quick Status Checklist

- [ ] **Step 1**: Checked logs - no `DJANGO_SECRET_KEY` error
- [ ] **Step 2**: Set `DJANGO_SECRET_KEY` in Railway variables
- [ ] **Step 3**: Linked PostgreSQL database (`DATABASE_URL`)
- [ ] **Step 4**: Ran database migrations
- [ ] **Step 5**: Created superuser (admin account)
- [ ] **Step 6**: Exposed service (got public URL)
- [ ] **Step 7**: Tested app - everything works
- [ ] **Step 8**: Set up Celery worker (optional)

---

## 🚨 Troubleshooting

### Service Still Crashing?

**Check Logs**:
1. Go to "Logs" tab
2. Look for the latest error message
3. Common issues:
   - Missing environment variables → Add them
   - Database connection failed → Link PostgreSQL
   - Migration errors → Run migrations manually

### Can't Access App?

**Check**:
1. Service is "Running" (green status)
2. Service is exposed (has public domain)
3. Check "Settings" → "Networking" for domain

### Migrations Failed?

**Fix**:
```powershell
# Run migrations manually
railway run python manage.py migrate

# If still failing, check database connection
railway run python manage.py dbshell
```

### Can't Create Superuser?

**Fix**:
```powershell
# Make sure you're linked to correct project
railway link

# Try creating superuser again
railway run python manage.py createsuperuser
```

---

## 🎯 Next Actions (Priority Order)

1. **✅ Check Logs** - See if service is running or has errors
2. **✅ Set `DJANGO_SECRET_KEY`** - If not already set
3. **✅ Link PostgreSQL** - If database connection error
4. **✅ Run Migrations** - Set up database tables
5. **✅ Create Superuser** - Admin account
6. **✅ Expose Service** - Get public URL
7. **✅ Test App** - Verify everything works
8. **✅ Set Up Celery** - Optional but recommended

---

## 📝 Quick Reference Commands

```powershell
# Login to Railway
railway login

# Link to project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# View logs
railway logs

# Open app in browser
railway open
```

---

**Last Updated**: 2025
**Status**: ✅ **Deployment Successful - Ready for Next Steps!**

