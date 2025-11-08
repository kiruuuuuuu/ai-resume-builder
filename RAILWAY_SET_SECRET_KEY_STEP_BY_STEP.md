# Step-by-Step: Set DJANGO_SECRET_KEY in Railway

## 🔴 Problem

Your service is crashing because `DJANGO_SECRET_KEY` is not set in Railway environment variables.

---

## ✅ Solution: Add DJANGO_SECRET_KEY to Railway

### Step 1: Go to Variables Tab

1. **In Railway Dashboard**, click on your service: **`ai-resume-builder`**
2. **Click "Variables" tab** (top navigation, next to "Deployments")
3. You should see a list of variables

### Step 2: Add DJANGO_SECRET_KEY

**Option A: If Variable Doesn't Exist**

1. **Click "New Variable" button** (usually at the top right or bottom of the variables list)
2. **Enter Variable Name**:
   - **Name**: `DJANGO_SECRET_KEY` (exactly as shown, case-sensitive, with underscores)
   - **DO NOT** use: `SECRET_KEY`, `django_secret_key`, `DJANGO_SECRETKEY`
3. **Enter Variable Value**:
   - **Value**: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`
   - Copy and paste this exact value
4. **Click "Add" or "Save"** button
5. **Verify**: The variable should appear in the list

**Option B: If Variable Already Exists**

1. **Find `DJANGO_SECRET_KEY`** in the variables list
2. **Click the edit icon** (pencil icon) next to it
3. **Update the value**:
   - **Value**: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`
4. **Click "Save"**
5. **Verify**: The value should be updated

### Step 3: Verify Variable is Set

1. **Check Variables List**:
   - Look for `DJANGO_SECRET_KEY` in the list
   - Verify the value is the long string (not empty)
   - Verify the name is exactly `DJANGO_SECRET_KEY` (case-sensitive)

2. **Common Mistakes to Avoid**:
   - ❌ Wrong name: `SECRET_KEY` (missing `DJANGO_` prefix)
   - ❌ Wrong case: `django_secret_key` (should be uppercase)
   - ❌ Missing underscores: `DJANGO_SECRETKEY` (should have underscore)
   - ❌ Empty value: Make sure the value field is not empty
   - ✅ Correct: `DJANGO_SECRET_KEY` with value `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`

### Step 4: Wait for Auto-Redeploy

**After adding/updating the variable**:

1. **Railway automatically detects the change**
2. **A new deployment should start automatically** (within 1-2 minutes)
3. **Check "Deployments" tab**:
   - You should see a new deployment starting
   - Wait for it to complete

**If it doesn't auto-redeploy**:
1. Go to "Deployments" tab
2. Click "Redeploy" button (or manually trigger a new deployment)

### Step 5: Check Logs

**After redeploy**:

1. **Go to "Logs" tab**
2. **Check for errors**:
   - ✅ **Success**: No more `DJANGO_SECRET_KEY` errors
   - ✅ **Success**: Should see Django server starting
   - ❌ **Error**: If you still see the error, go to Troubleshooting below

---

## 🔧 Troubleshooting

### Problem 1: Variable Not Appearing in List

**Check**:
1. Did you click "Add" or "Save" after entering the value?
2. Try refreshing the page
3. Check if you're in the correct service (should be `ai-resume-builder`)

**Fix**:
1. Delete the variable (if it exists)
2. Add it again with exact name: `DJANGO_SECRET_KEY`
3. Make sure the value is not empty

### Problem 2: Still Getting Error After Adding Variable

**Check**:
1. Variable name is exactly `DJANGO_SECRET_KEY` (case-sensitive)
2. Variable value is not empty
3. Service has been redeployed after adding the variable

**Fix**:
1. **Delete the variable** and re-add it
2. **Manually trigger redeploy**:
   - Go to "Deployments" tab
   - Click "Redeploy" button
3. **Check logs** again after redeploy

### Problem 3: Wrong Variable Name

**Common mistakes**:
- ❌ `SECRET_KEY` → Should be `DJANGO_SECRET_KEY`
- ❌ `django_secret_key` → Should be `DJANGO_SECRET_KEY` (uppercase)
- ❌ `DJANGO_SECRETKEY` → Should be `DJANGO_SECRET_KEY` (with underscore)

**Fix**:
1. Delete the wrong variable
2. Add a new variable with exact name: `DJANGO_SECRET_KEY`

### Problem 4: Variable Value is Empty

**Check**:
1. Did you paste the value correctly?
2. Is there any extra spaces or characters?

**Fix**:
1. Click edit icon (pencil) next to the variable
2. Paste the value again: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`
3. Make sure there are no spaces before or after
4. Click "Save"

### Problem 5: Service Not Redeploying

**Check**:
1. Did Railway detect the variable change?
2. Is there a new deployment in "Deployments" tab?

**Fix**:
1. **Manually trigger redeploy**:
   - Go to "Deployments" tab
   - Click "Redeploy" button
   - Wait for deployment to complete
2. **Check logs** after redeploy

---

## 📝 Quick Checklist

- [ ] Went to "Variables" tab in Railway Dashboard
- [ ] Added/updated `DJANGO_SECRET_KEY` variable
- [ ] Variable name is exactly `DJANGO_SECRET_KEY` (case-sensitive)
- [ ] Variable value is: `(1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u`
- [ ] Variable appears in the list with correct name and value
- [ ] Service redeployed (automatic or manual)
- [ ] Checked logs - no more `DJANGO_SECRET_KEY` error
- [ ] Service status is "Running" (green)

---

## 🎯 Expected Result

**After setting `DJANGO_SECRET_KEY`**:

1. ✅ Variable appears in "Variables" tab
2. ✅ Service automatically redeploys
3. ✅ No more `DJANGO_SECRET_KEY` error in logs
4. ✅ Service starts successfully
5. ✅ Service status is "Running" (green)

---

## 📸 Visual Guide

### Step 1: Variables Tab
```
Railway Dashboard
├── ai-resume-builder (your service)
    ├── Deployments tab
    ├── Variables tab ← CLICK HERE
    ├── Metrics tab
    └── Settings tab
```

### Step 2: Add Variable
```
Variables Tab
├── [New Variable] button ← CLICK HERE
│   ├── Name: DJANGO_SECRET_KEY
│   ├── Value: (1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u
│   └── [Add] button ← CLICK HERE
```

### Step 3: Verify
```
Variables List
├── DJANGO_SECRET_KEY: (1$9--ym&be&7oigv0+nz&me9z5f2f=3uauue)p=@y34k=2z1u ✓
├── DEBUG: False
├── ALLOWED_HOSTS: *.railway.app
└── ... (other variables)
```

---

## 🚀 Next Steps After Fixing

Once `DJANGO_SECRET_KEY` is set and service is running:

1. ✅ **Link PostgreSQL Database** (if not already)
2. ✅ **Run Migrations**: `railway run python manage.py migrate`
3. ✅ **Create Superuser**: `railway run python manage.py createsuperuser`
4. ✅ **Expose Service**: Get public URL from "Settings" → "Networking"
5. ✅ **Test Your App**: Open URL in browser

---

**Last Updated**: 2025
**Status**: ⚠️ **CRITICAL - Must Fix Before Service Can Start**

