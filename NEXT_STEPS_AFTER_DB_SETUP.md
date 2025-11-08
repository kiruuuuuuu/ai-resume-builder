# Next Steps After PostgreSQL Setup

## ✅ Current Status

- ✅ PostgreSQL service created and running
- ✅ Database is empty (no tables) - **This is normal!**
- ⚠️ Need to run migrations to create tables

---

## 🔗 Step 1: Link PostgreSQL to Django Service

### In Railway Dashboard:

1. **Click on `ai-resume-builder` service** (not Postgres)
2. **Go to "Variables" tab**
3. **Click "Reference Variable" button**
4. **Select "Postgres" service** from dropdown
5. **Select `DATABASE_URL`** from variable list
6. **Click "Add"**
7. **Wait for redeploy** (automatic, 1-2 minutes)

**Verify**:
- `DATABASE_URL` should appear in your Django service variables
- Service should automatically redeploy

---

## 🗃️ Step 2: Run Database Migrations

### Using Railway CLI:

**Open PowerShell** in your project directory:

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
  Applying jobs.0001_initial... OK
  Applying pages.0001_bugreport... OK
  ...
```

**After migrations**:
- Go back to Railway Dashboard → Postgres service → "Database" tab
- You should now see tables created! ✅

---

## 👤 Step 3: Create Superuser (Admin Account)

**Using Railway CLI**:

```powershell
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

## 🌐 Step 4: Expose Service (Get Public URL)

### In Railway Dashboard:

1. **Click on `ai-resume-builder` service**
2. **Go to "Settings" tab**
3. **Scroll to "Networking" section**
4. **Click "Generate Domain" button**
   - Railway will generate a free domain like: `ai-resume-builder-production.up.railway.app`
5. **Copy the domain** (you'll need this)

---

## ✅ Step 5: Verify Everything Works

### Test Your App:

1. **Open your Railway domain** in browser:
   - Example: `https://ai-resume-builder-production.up.railway.app`

2. **Test Features**:
   - [ ] Home page loads
   - [ ] User registration works
   - [ ] User login works
   - [ ] Resume builder works
   - [ ] PDF generation works
   - [ ] Admin dashboard: `https://your-domain.railway.app/users/admin-login/`

### Verify Database Tables:

1. **Go to Railway Dashboard → Postgres service → "Database" tab**
2. **You should now see tables**:
   - `users_customuser`
   - `resumes_resume`
   - `jobs_jobposting`
   - `pages_bugreport`
   - And other Django tables

---

## 🚨 Troubleshooting

### Migrations Failed?

**Check**:
1. Is `DATABASE_URL` linked to Django service?
2. Check logs for errors: Railway Dashboard → `ai-resume-builder` → "Logs" tab

**Fix**:
```powershell
# Check if DATABASE_URL is set
railway variables

# Run migrations again
railway run python manage.py migrate
```

### Can't Create Superuser?

**Fix**:
```powershell
# Make sure you're linked to correct project
railway link

# Try creating superuser again
railway run python manage.py createsuperuser
```

### Database Still Empty After Migrations?

**Check**:
1. Did migrations run successfully? (check output)
2. Are you looking at the correct database?
3. Try running migrations again

---

## 📝 Quick Checklist

- [ ] **Step 1**: Linked `DATABASE_URL` from Postgres to Django service
- [ ] **Step 2**: Ran migrations (`railway run python manage.py migrate`)
- [ ] **Step 3**: Verified tables created in Postgres "Database" tab
- [ ] **Step 4**: Created superuser (`railway run python manage.py createsuperuser`)
- [ ] **Step 5**: Exposed service (got public URL)
- [ ] **Step 6**: Tested app - everything works

---

**Last Updated**: 2025
**Status**: ✅ **Ready to Run Migrations!**

