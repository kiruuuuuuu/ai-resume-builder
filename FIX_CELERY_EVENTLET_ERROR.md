# Fix Celery Eventlet Error - Switch to Prefork Pool

## ❌ Problem

**Error in Celery Worker Logs**:
```
RuntimeError: do not call blocking functions from the mainloop
```

**Root Cause**:
- Eventlet pool has compatibility issues with Redis connections
- Eventlet monkey patching conflicts with blocking I/O operations
- This causes the worker to crash when processing tasks

---

## ✅ Solution

**Switch from `eventlet` pool to `prefork` pool (default)**:
- ✅ **More stable** with Redis
- ✅ **No monkey patching** needed (avoids conflicts)
- ✅ **Better compatibility** with Django and Celery
- ✅ **Production-ready** and widely used

---

## 🔧 Fix Steps

### Step 1: Update Celery Worker Start Command in Railway

**In Railway Dashboard**:

1. **Go to your Celery worker service**
2. **Click "Settings" → "Deploy"**
3. **Update "Start Command"** from:
   ```bash
   celery -A core worker -l info -P eventlet --concurrency=10
   ```
   **To**:
   ```bash
   celery -A core worker -l info --concurrency=4
   ```
   **Note**: Prefork pool is the default, so we don't need `-P prefork`.

4. **Click "Save"**
5. **Wait for redeploy** (automatic)

---

### Step 2: Verify Fix

**Check Celery Worker Logs**:

1. **Go to Celery worker service**
2. **Click "Logs" tab**
3. **Look for**:
   ```
   ℹ Using prefork pool (default, no monkey patching)
   celery@v1 ready.
   ```

**✅ Success Signs**:
- ✅ No `RuntimeError` errors
- ✅ Worker stays running (doesn't crash)
- ✅ `celery@v1 ready.` message appears
- ✅ Can process tasks without crashing

**❌ If Still Errors**:
- Check that start command is updated (no `-P eventlet`)
- Verify Redis connection is working
- Check environment variables are set correctly

---

## 📊 Pool Comparison

### Prefork Pool (Default) ✅ **Recommended**
- **Stability**: ⭐⭐⭐⭐⭐ Excellent
- **Redis Compatibility**: ⭐⭐⭐⭐⭐ Perfect
- **Concurrency**: Multiple processes (fork-based)
- **Memory Usage**: Higher (each process has its own memory)
- **Best For**: Production, stability, Redis

### Eventlet Pool ❌ **Not Recommended (Causes Errors)**
- **Stability**: ⭐⭐ Poor (conflicts with Redis)
- **Redis Compatibility**: ⭐⭐ Poor (blocking I/O issues)
- **Concurrency**: Green threads (lightweight)
- **Memory Usage**: Lower
- **Best For**: Not recommended for this project

### Threads Pool (Alternative)
- **Stability**: ⭐⭐⭐⭐ Good
- **Redis Compatibility**: ⭐⭐⭐⭐ Good
- **Concurrency**: Threads (shared memory)
- **Memory Usage**: Lower than prefork
- **Best For**: Higher concurrency needs

---

## 🎯 Alternative: Use Threads Pool (If You Need Higher Concurrency)

**If you need higher concurrency** (more than 4 workers):

**Update Start Command to**:
```bash
celery -A core worker -l info -P threads --concurrency=10
```

**Pros**:
- ✅ Higher concurrency (10+ workers)
- ✅ Lower memory usage than prefork
- ✅ Good Redis compatibility
- ✅ No monkey patching needed

**Cons**:
- ⚠️ Slightly less stable than prefork
- ⚠️ Python's GIL limits CPU-bound tasks

---

## 📝 Code Changes Made

### 1. Updated `core/__init__.py`
- ✅ Only applies eventlet monkey patching when explicitly requested
- ✅ No automatic eventlet patching on Linux
- ✅ Defaults to prefork pool (no monkey patching)

### 2. Updated `RAILWAY_DEPLOYMENT_GUIDE.md`
- ✅ Changed start command to use prefork pool
- ✅ Added notes about pool stability
- ✅ Updated troubleshooting section

---

## 🧪 Test the Fix

**After updating the start command**:

1. **Generate a PDF resume** in your app
2. **Check Celery worker logs** - should see task execution:
   ```
   [INFO] Task resumes.tasks.generate_resume_pdf_task[...] received
   [INFO] Task resumes.tasks.generate_resume_pdf_task[...] succeeded
   ```
3. **Verify no crashes** - worker should stay running

---

## ✅ Summary

**What Changed**:
- ✅ Celery worker now uses **prefork pool** (default, most stable)
- ✅ **No eventlet monkey patching** (prevents Redis conflicts)
- ✅ **Better compatibility** with Redis and Django
- ✅ **Production-ready** configuration

**What You Need to Do**:
1. ✅ Update start command in Railway (remove `-P eventlet`)
2. ✅ Verify worker is running without errors
3. ✅ Test task execution (generate a PDF)

---

## 🚀 Next Steps

1. **Update start command** in Railway (see Step 1 above)
2. **Check logs** to verify fix (see Step 2 above)
3. **Test tasks** by generating a PDF resume
4. **Monitor** worker logs for any issues

---

**The fix is applied in the code. Just update the start command in Railway!**

