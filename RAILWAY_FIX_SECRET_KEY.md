# Fix: DJANGO_SECRET_KEY Not Set Error

## 🔴 Error

```
ValueError: DJANGO_SECRET_KEY environment variable is not set! 
This is required for security. Please set it in your .env file or environment variables.
```

## ✅ Solution: Add DJANGO_SECRET_KEY to Railway

### Step 1: Generate a New SECRET_KEY

I've generated a new SECRET_KEY for you:

```
(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u
```

**Or generate your own**:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 2: Add to Railway Dashboard

1. **Go to Railway Dashboard**:
   - Open your project: `ai-resume-builder`
   - Click on your service (the one that's crashing)

2. **Go to "Variables" Tab**:
   - Click "Variables" tab at the top
   - Look for `DJANGO_SECRET_KEY` in the list

3. **Add/Update Variable**:
   - If `DJANGO_SECRET_KEY` exists: Click the edit icon (pencil) and update the value
   - If `DJANGO_SECRET_KEY` doesn't exist: Click "New Variable" button
   - **Variable Name**: `DJANGO_SECRET_KEY` (exactly as shown, case-sensitive)
   - **Variable Value**: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u` (or your generated key)
   - Click "Add" or "Save"

4. **Important**: Make sure the variable name is **exactly** `DJANGO_SECRET_KEY` (not `SECRET_KEY` or `django_secret_key`)

### Step 3: Verify Variable is Set

**Check Variables List**:
- You should see `DJANGO_SECRET_KEY` in the list
- The value should be the long string you just added

### Step 4: Redeploy Service

**After adding the variable, Railway should automatically redeploy**:
- Wait 1-2 minutes
- Check the "Deployments" tab
- Look for a new deployment starting

**If it doesn't auto-redeploy**:
- Go to "Deployments" tab
- Click "Redeploy" button (or manually trigger a new deployment)

### Step 5: Check Logs

**After redeploy, check logs**:
1. Go to "Logs" tab
2. Look for successful startup (no more `DJANGO_SECRET_KEY` errors)
3. Should see: "Starting server..." or similar success messages

---

## 🔍 Troubleshooting

### Variable Not Saving?

**Check**:
1. Make sure you clicked "Add" or "Save" after entering the value
2. Check if the variable appears in the list
3. Try refreshing the page and checking again

### Still Getting Error?

**Verify**:
1. Variable name is exactly `DJANGO_SECRET_KEY` (case-sensitive)
2. Variable value is not empty
3. Service has been redeployed after adding the variable

**Try**:
1. Delete the variable and re-add it
2. Redeploy the service manually
3. Check logs again

### Wrong Variable Name?

**Common mistakes**:
- ❌ `SECRET_KEY` (wrong - missing `DJANGO_` prefix)
- ❌ `django_secret_key` (wrong - should be uppercase)
- ❌ `DJANGO_SECRETKEY` (wrong - missing underscore)
- ✅ `DJANGO_SECRET_KEY` (correct!)

---

## 📝 Quick Checklist

- [ ] Generated SECRET_KEY
- [ ] Added `DJANGO_SECRET_KEY` to Railway variables
- [ ] Verified variable name is correct (case-sensitive)
- [ ] Verified variable value is not empty
- [ ] Service redeployed (automatic or manual)
- [ ] Checked logs - no more errors
- [ ] Service status is "Running" (green)

---

## 🎯 Expected Result

After adding `DJANGO_SECRET_KEY`:
- ✅ Service should start successfully
- ✅ No more `ValueError: DJANGO_SECRET_KEY environment variable is not set!` errors
- ✅ Service status should be "Running" (green)
- ✅ Logs should show successful startup

---

**Last Updated**: 2025

