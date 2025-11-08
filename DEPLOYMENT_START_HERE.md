# Deployment - Start Here! 🚀

## 📍 Where to Open PowerShell/CMD

### Open PowerShell/CMD in Your Project Directory

**Your Project Path**:
```
C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0
```

---

## 🎯 Step-by-Step: Opening PowerShell/CMD

### Method 1: Open PowerShell in Project Folder (Easiest)

1. **Open File Explorer**
2. **Navigate to**: `C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0`
3. **Right-click** in the folder (empty space)
4. **Select**: "Open in Terminal" or "Open PowerShell window here"
5. **Done!** ✅ You're now in the correct directory

### Method 2: Open PowerShell and Navigate

1. **Open PowerShell** (search "PowerShell" in Windows)
2. **Run this command**:
   ```powershell
   cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"
   ```
3. **Verify you're in the right place**:
   ```powershell
   pwd
   # Should show: C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0
   ```
4. **Done!** ✅

### Method 3: From VS Code/Your Editor

If you're using VS Code or another editor:

1. **Open the project** in your editor
2. **Open integrated terminal** (usually `Ctrl + ~` or `Ctrl + ``)
3. **You're already in the project directory!** ✅

---

## ✅ Verify You're in the Right Place

**Run this command** to verify:
```powershell
# Check current directory
pwd

# List files (should see manage.py, requirements.txt, etc.)
ls

# Or on Windows CMD:
dir
```

**You should see**:
- `manage.py`
- `requirements.txt`
- `Dockerfile`
- `DEPLOYMENT_GUIDE.md`
- `core/` folder
- `resumes/` folder
- etc.

---

## 🚀 Quick Start Commands

**Once you're in the project directory**, start with:

```powershell
# 1. Verify you're in the right place
pwd

# 2. Install Fly CLI (if not installed)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# 3. Verify Fly CLI
fly version

# 4. Login to Fly.io
fly auth login

# 5. Continue with deployment...
```

---

## 📝 Full Path Reference

**Your Project Path**:
```
C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0
```

**Copy this path** and use it in:
- File Explorer (to navigate)
- PowerShell/CMD (with `cd` command)
- Any file operations

---

## ⚠️ Important Notes

1. **Always start in project directory** - All `fly` commands should be run from here
2. **Don't navigate away** - Stay in this directory for all deployment commands
3. **If you get lost** - Run `cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"` to return

---

## 🎯 Summary

**Open PowerShell/CMD in**:
```
C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0
```

**Easiest Method**: Right-click folder → "Open in Terminal" or "Open PowerShell window here"

**Then run all deployment commands from there!**

---

**Next Step**: Install Fly CLI and start deployment! 🚀

