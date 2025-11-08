# Deployment Quick Start - Step-by-Step

## 🎯 Overview

**Yes, you use your computer's command line (PowerShell/CMD) for all deployment steps!**

All commands in the deployment guide are run on **YOUR COMPUTER** using:
- **Windows**: PowerShell or CMD
- **macOS/Linux**: Terminal

You don't need to SSH into Fly.io until after deployment (and only for verification).

---

## 📋 Step-by-Step Process

### Step 1: Create Fly.io Account (Browser)

1. Go to https://fly.io in your **browser**
2. Sign up with GitHub, Google, or email
3. Verify your email
4. **Done in browser** ✅

### Step 2: Install Fly CLI (Your Computer - PowerShell/CMD)

**Open PowerShell or CMD on your computer** and run:

```powershell
# Install Fly CLI (Windows PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Verify installation**:
```powershell
fly version
```

### Step 3: Login to Fly.io (Your Computer - PowerShell/CMD)

**Still in your computer's PowerShell/CMD**, run:

```powershell
fly auth login
```

This will:
- Open your browser automatically
- Ask you to authorize
- Return to PowerShell/CMD when done

### Step 4: All Deployment Commands (Your Computer - PowerShell/CMD)

**All remaining commands are run on YOUR COMPUTER**:

```powershell
# Navigate to your project
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"

# Initialize Fly.io app
fly launch

# Create database
fly postgres create

# Create Redis
fly redis create

# Set secrets
fly secrets set DJANGO_SECRET_KEY="..."

# Deploy
fly deploy
```

**All of these run in YOUR PowerShell/CMD window!**

---

## 🔍 When Do You Use Fly.io Console?

### You DON'T need to SSH/Console for deployment

**You only use Fly.io console for**:
- ✅ Verification after deployment
- ✅ Running migrations (can also be done via `fly ssh console`)
- ✅ Creating superuser
- ✅ Debugging issues

**Example** (after deployment):
```powershell
# SSH into your deployed app (from YOUR computer)
fly ssh console

# Now you're in the Fly.io machine
# Run commands like:
python manage.py migrate
python manage.py createsuperuser
```

---

## 📝 Complete Workflow

### On Your Computer (PowerShell/CMD):

1. ✅ Install Fly CLI
2. ✅ Login: `fly auth login`
3. ✅ Initialize app: `fly launch`
4. ✅ Create database: `fly postgres create`
5. ✅ Create Redis: `fly redis create`
6. ✅ Set secrets: `fly secrets set ...`
7. ✅ Deploy: `fly deploy`
8. ✅ Verify: `fly status`, `fly logs`

### In Browser:

1. ✅ Create Fly.io account
2. ✅ Authorize CLI (when `fly auth login` opens browser)

### In Fly.io Console (Optional - Only for Verification):

1. ⏳ SSH: `fly ssh console` (from your computer)
2. ⏳ Run migrations: `python manage.py migrate`
3. ⏳ Create superuser: `python manage.py createsuperuser`

---

## 🎯 Quick Answer

**Question**: Should I use my computer CMD after creating an account?

**Answer**: **YES!** 

- ✅ Create account in **browser**
- ✅ Install Fly CLI on **your computer**
- ✅ Login from **your computer** (PowerShell/CMD)
- ✅ Run ALL deployment commands from **your computer** (PowerShell/CMD)
- ✅ Only SSH into Fly.io for verification (optional)

---

## 💡 Important Notes

1. **All `fly` commands** run on YOUR computer
2. **Fly CLI** connects to Fly.io from your computer
3. **No need to SSH** until after deployment (and only for verification)
4. **Browser** is only used for account creation and authorization

---

## 🚀 Example Session

```powershell
# 1. Open PowerShell on YOUR computer
# 2. Navigate to project
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"

# 3. Install Fly CLI (if not installed)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# 4. Login (opens browser, then returns to PowerShell)
fly auth login

# 5. Initialize app (all in PowerShell)
fly launch

# 6. Create resources (all in PowerShell)
fly postgres create
fly redis create

# 7. Set secrets (all in PowerShell)
fly secrets set DJANGO_SECRET_KEY="your-key"

# 8. Deploy (all in PowerShell)
fly deploy

# 9. Verify (all in PowerShell)
fly status
fly logs
```

**Everything runs in YOUR PowerShell window!**

---

## ✅ Summary

- **Browser**: Only for account creation
- **Your Computer (PowerShell/CMD)**: For ALL deployment commands
- **Fly.io Console**: Only for verification (optional)

**Start with**: Your computer's PowerShell/CMD after creating the account!

---

**For detailed steps, see**: `DEPLOYMENT_GUIDE.md`

