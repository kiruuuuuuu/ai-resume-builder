# How to Create Superuser on Railway

## ❌ Problem

When running `railway run python manage.py createsuperuser` from your local Windows machine, you get:
```
could not translate host name "postgres.railway.internal" to address: No such host is known.
```

**Why**: Railway's internal hostnames (`postgres.railway.internal`) are only accessible from within Railway's network, not from your local machine.

---

## ✅ Solution: Use Railway's Web Terminal (Recommended)

### Method 1: Railway Web Terminal (Easiest)

1. **Go to Railway Dashboard**
   - Open your Railway project
   - Click on your **Django app service** (not Celery worker)

2. **Open Web Terminal**
   - Click on the **"Deployments"** tab
   - Click on the latest deployment
   - Click **"View Logs"** or look for **"Terminal"** / **"Console"** option
   - OR: Go to **"Settings"** → Look for **"Console"** or **"Terminal"** option

3. **Run Createsuperuser Command**
   ```bash
   python manage.py createsuperuser
   ```

4. **Follow Prompts**
   - Enter username
   - Enter email
   - Enter password (twice)

---

### Method 2: Railway CLI with Service Selection

1. **Make sure you're linked to the correct service**
   ```bash
   railway link
   ```
   - Select your **Django app service** (not PostgreSQL or Redis)

2. **Run createsuperuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

   **Note**: This should work if Railway CLI is properly configured and you're linked to the Django service.

---

### Method 3: Create Superuser via Django Shell (Alternative)

1. **Open Railway Web Terminal** (see Method 1)

2. **Run Django Shell**
   ```bash
   python manage.py shell
   ```

3. **Create Superuser in Python**
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   User.objects.create_superuser('admin', 'admin@example.com', 'your-password-here')
   ```

4. **Exit Shell**
   ```python
   exit()
   ```

---

## 🔍 Troubleshooting

### Issue: `railway run` not working from Windows

**Solution**: Use Railway's web terminal instead (Method 1)

### Issue: Can't find Terminal/Console in Railway

**Solution**: 
- Look for **"Deployments"** → **"View Logs"** → **"Terminal"** tab
- Or use Railway CLI: `railway shell` (if available)

### Issue: Database connection errors

**Solution**:
- Make sure you're running the command in Railway's environment (web terminal)
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` is set correctly in Railway variables

---

## 📝 Quick Steps (Recommended)

1. **Go to Railway Dashboard**
2. **Click on Django app service**
3. **Open Web Terminal** (Deployments → Terminal/Console)
4. **Run**: `python manage.py createsuperuser`
5. **Enter**: username, email, password
6. **Done!**

---

## 🎯 After Creating Superuser

1. **Access Django Admin**
   - Go to your Railway app URL
   - Navigate to: `https://your-app.railway.app/admin/`
   - Login with your superuser credentials

2. **Access Admin Dashboard** (Custom)
   - Navigate to: `https://your-app.railway.app/admin/login/`
   - Login with your superuser credentials

---

## ✅ Summary

**Best Method**: Use Railway's web terminal to create superuser
- ✅ Works directly in Railway's environment
- ✅ Has access to internal network addresses
- ✅ No local configuration needed
- ✅ Simple and straightforward

**Alternative**: Use Railway CLI if properly configured
- ⚠️ Requires proper linking to Django service
- ⚠️ May have network access issues from Windows

---

**Use Railway's web terminal - it's the easiest and most reliable method!** 🎉

