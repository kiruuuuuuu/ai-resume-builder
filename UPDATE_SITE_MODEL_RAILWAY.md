# 🔧 Update Django Site Model on Railway

**Your Railway Domain**: `ai-resume-builder-jk.up.railway.app`

## ⚡ Quick Fix (3 Methods)

### Method 1: Using Railway CLI (Recommended)

**Prerequisites:**
- Railway CLI installed: `npm install -g @railway/cli`
- Logged into Railway: `railway login`

**Steps:**

1. **Login to Railway**:
   ```bash
   railway login
   ```

2. **Link to your project** (if not already linked):
   ```bash
   railway link
   ```
   - Select your project when prompted

3. **Run the command on Railway servers**:
   ```bash
   railway run python manage.py shell
   ```

4. **In the Python shell, run**:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ai-resume-builder-jk.up.railway.app'
   site.name = 'AI Resume Builder'
   site.save()
   print(f'✅ Site updated: {site.domain}')
   exit()
   ```

**Alternative: Single Command**:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

---

### Method 2: Using Railway Web Interface (Easier)

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your project** → **Your Django service**
3. **Go to "Deployments" tab**
4. **Click on the latest deployment**
5. **Click "View Logs"** or **"Terminal"** (if available)
6. **Or use "Settings" → "Console"** (if available)
7. **Run the command**:
   ```bash
   python manage.py shell
   ```
8. **In the Python shell**:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get(id=1)
   site.domain = 'ai-resume-builder-jk.up.railway.app'
   site.name = 'AI Resume Builder'
   site.save()
   print('✅ Site updated!')
   exit()
   ```

---

### Method 3: Using Django Admin (Easiest - If Admin Access Available)

1. **Go to**: https://ai-resume-builder-jk.up.railway.app/admin/
2. **Login** with your superuser account
3. **Navigate to**: **Sites** → **Sites**
4. **Click on the site** (usually ID=1, "example.com")
5. **Update**:
   - **Domain name**: `ai-resume-builder-jk.up.railway.app`
   - **Display name**: `AI Resume Builder`
6. **Click Save**

---

## 🔍 Verify Site Model

**Check current Site domain**:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(f'Domain: {Site.objects.get(id=1).domain}')"
```

**Expected output**:
```
Domain: ai-resume-builder-jk.up.railway.app
```

---

## 🚨 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'django'"

**Cause**: Command is running locally instead of on Railway servers.

**Solution**:
1. Make sure you're using `railway run` command (not just `python`)
2. Verify Railway CLI is installed: `railway --version`
3. Verify you're logged in: `railway whoami`
4. Verify you're linked to the project: `railway link`

### Error: "railway: command not found"

**Solution**:
1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```
2. Or download from: https://github.com/railwayapp/cli/releases

### Error: "Not linked to a project"

**Solution**:
```bash
railway link
```
- Select your project when prompted

### Can't Access Railway Web Terminal

**Solution**: Use Django Admin (Method 3) instead, or use Railway CLI (Method 1).

---

## ✅ Quick Reference

**Command to update Site model**:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(id=1); site.domain = 'ai-resume-builder-jk.up.railway.app'; site.name = 'AI Resume Builder'; site.save(); print('✅ Site updated!')"
```

**Verify Site model**:
```bash
railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1).domain)"
```

**Expected domain**: `ai-resume-builder-jk.up.railway.app`

---

**Last Updated**: 2025

