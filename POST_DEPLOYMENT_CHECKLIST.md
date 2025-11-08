# Post-Deployment Checklist - Railway.app

Complete step-by-step guide for what to do after adding environment variables in Railway.

---

## ✅ Step 1: Check Deployment Status

### In Railway Dashboard:

1. **Go to your service**: Click on `ai-resume-builder` service
2. **Check Status**: 
   - ✅ **Green "Running"** = Service is live!
   - ❌ **Red "Crashed"** = Check logs (Step 2)
   - ⏳ **Yellow "Deploying"** = Wait for deployment to finish

3. **Check Activity Panel** (right side):
   - Look for "Deployment successful" message
   - Check for any error messages

---

## ✅ Step 2: View Logs (If Service Crashed)

### In Railway Dashboard:

1. **Click "Logs" tab** (top navigation)
2. **Check for errors**:
   - Look for red error messages
   - Common issues:
     - `DJANGO_SECRET_KEY not set` → Add it to variables
     - `Database connection failed` → Check `DATABASE_URL`
     - `Module not found` → Check `requirements.txt`
     - `Migration errors` → Run migrations (Step 3)

### Common Errors & Fixes:

**Error**: `ValueError: DJANGO_SECRET_KEY environment variable is not set!`
- **Fix**: Add `DJANGO_SECRET_KEY` to Railway variables

**Error**: `django.db.utils.OperationalError: could not connect to server`
- **Fix**: Link PostgreSQL service to your Django service (Variables → Reference Variable)

**Error**: `ModuleNotFoundError: No module named 'xxx'`
- **Fix**: Check `requirements.txt` includes all packages

---

## ✅ Step 3: Run Database Migrations

### Option A: Using Railway Dashboard (Recommended)

1. **Go to your service** → "Deployments" tab
2. **Click on latest deployment** → "View Logs"
3. **Check if migrations ran automatically** (look for "Running migrations...")
4. **If migrations didn't run**, use Option B below

### Option B: Using Railway CLI

**Open PowerShell** in your project directory:

```powershell
# Make sure you're in the project directory
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"

# Login to Railway (if not already)
railway login

# Link to your project (if not already linked)
railway link

# Run migrations
railway run python manage.py migrate
```

**Expected Output**:
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying ... OK
```

---

## ✅ Step 4: Create Superuser (Admin Account)

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
- **Email**: `admin@example.com` (optional)
- **Password**: Enter a strong password (twice)

**Expected Output**:
```
Superuser created successfully.
```

---

## ✅ Step 5: Verify Service is Running

### In Railway Dashboard:

1. **Check Service Status**: Should be "Running" (green)
2. **Get Your App URL**:
   - Go to "Settings" → "Domains"
   - Copy your Railway domain (e.g., `https://ai-resume-builder-production.up.railway.app`)

### Test Your App:

1. **Open your app URL** in browser
2. **Check Home Page**: Should load without errors
3. **Test Features**:
   - ✅ Home page loads
   - ✅ User registration works
   - ✅ User login works
   - ✅ Resume builder works
   - ✅ PDF generation works

---

## ✅ Step 6: Set Up Celery Worker (Optional but Recommended)

**Why**: Celery handles async tasks like PDF generation.

### In Railway Dashboard:

1. **Create New Service**:
   - Click "New" → "Empty Service"
   - Name it: `celery-worker`

2. **Connect to GitHub**:
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure Service**:
   - Go to "Settings" → "Deploy"
   - Set "Start Command":
     ```
     celery -A core worker -l info -P eventlet --concurrency=10
     ```

4. **Add Environment Variables**:
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

5. **Verify Worker is Running**:
   - Go to "Logs" tab
   - Should see: `celery@v1 ready.`

---

## ✅ Step 7: Test Admin Dashboard

### Access Admin Login:

1. **Go to your app URL**: `https://your-app.railway.app`
2. **Navigate to**: `https://your-app.railway.app/users/admin-login/`
3. **Login** with superuser credentials (from Step 4)
4. **Verify Dashboard**:
   - ✅ Bug reports section visible
   - ✅ User statistics visible
   - ✅ Resume statistics visible
   - ✅ System health visible

---

## ✅ Step 8: Final Verification

### Test All Features:

- [ ] **Home Page**: Loads correctly
- [ ] **User Registration**: Can create new account
- [ ] **User Login**: Can login with credentials
- [ ] **Resume Builder**: Can create/edit resume
- [ ] **PDF Generation**: Can download PDF
- [ ] **Admin Dashboard**: Can access and view stats
- [ ] **Bug Reporting**: Can submit bug reports
- [ ] **Static Files**: CSS/JS loading correctly
- [ ] **Media Files**: Profile photos uploading

### Check Railway Dashboard:

- [ ] **Service Status**: Running (green)
- [ ] **Logs**: No errors
- [ ] **Metrics**: CPU/Memory usage normal
- [ ] **Deployments**: Latest deployment successful

---

## 🚨 Troubleshooting

### Service Won't Start

**Check Logs**:
1. Go to "Logs" tab
2. Look for error messages
3. Common fixes:
   - Missing environment variables → Add them
   - Database connection failed → Link PostgreSQL service
   - Port conflict → Railway auto-handles this

### Migrations Failed

**Fix**:
```powershell
# Run migrations manually
railway run python manage.py migrate

# If still failing, check database connection
railway run python manage.py dbshell
```

### Can't Create Superuser

**Fix**:
```powershell
# Make sure you're linked to correct project
railway link

# Try creating superuser again
railway run python manage.py createsuperuser
```

### Celery Worker Not Running

**Check**:
1. Worker service status (should be "Running")
2. Worker logs (should show "celery@v1 ready")
3. Redis connection (check `REDIS_URL` is set)

**Fix**:
```powershell
# Check worker logs
railway logs --service celery-worker

# Restart worker service
# Go to Railway Dashboard → Worker Service → Redeploy
```

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

# Check Django settings
railway run python manage.py check --deploy

# View logs
railway logs

# View logs for specific service
railway logs --service ai-resume-builder

# Open app in browser
railway open
```

---

## ✅ Summary

**After adding environment variables, do this**:

1. ✅ **Check deployment status** (should be "Running")
2. ✅ **View logs** (check for errors)
3. ✅ **Run migrations** (`railway run python manage.py migrate`)
4. ✅ **Create superuser** (`railway run python manage.py createsuperuser`)
5. ✅ **Test your app** (open URL in browser)
6. ✅ **Set up Celery worker** (optional but recommended)
7. ✅ **Test admin dashboard** (login and verify)
8. ✅ **Final verification** (test all features)

---

## 🎉 Success!

If all steps are completed:
- ✅ Your app is live on Railway
- ✅ Database is set up
- ✅ Admin account is created
- ✅ All features are working
- ✅ App is ready for users!

---

## 📚 Next Steps

1. **Custom Domain** (optional): Set up custom domain in Railway
2. **Monitoring**: Set up monitoring/alerting
3. **Backups**: Configure database backups
4. **Scaling**: Scale services if needed
5. **Security**: Review security settings

---

**Last Updated**: 2025
**Status**: ✅ **Ready for Deployment!**

