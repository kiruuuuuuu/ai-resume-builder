# Admin Setup Guide

This guide explains how to create an admin user and access the admin dashboard.

## What is a Staff User?

In Django, there are two types of admin users:

1. **Staff User** (`is_staff=True`):
   - Can access the admin dashboard
   - Has limited permissions (can be customized)
   - Cannot access Django's default admin interface unless also superuser

2. **Superuser** (`is_superuser=True`):
   - Has `is_staff=True` automatically
   - Has ALL permissions (full access)
   - Can access both custom admin dashboard AND Django's default admin interface

**For this project**: Both staff users and superusers can access the custom admin dashboard at `/users/admin-dashboard/`.

---

## Method 1: Create a Superuser (Recommended)

This is the easiest way to create an admin account.

### Step 1: Open Terminal/Command Prompt

Navigate to your project directory:
```bash
cd "C:\Users\kiruk\OneDrive\Desktop\resume v2\AI_Resume_Builder v2.0"
```

### Step 2: Activate Virtual Environment (if using one)

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Run Django Management Command

```bash
python manage.py createsuperuser
```

### Step 4: Follow the Prompts

You'll be asked to enter:
- **Username**: Choose a username (e.g., `admin`)
- **Email address**: Enter your email (optional but recommended)
- **Password**: Enter a strong password (you'll be asked twice)

**Example**:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

**That's it!** You now have a superuser account that can access the admin dashboard.

---

## Method 2: Make an Existing User Staff

If you already have a user account and want to make it an admin:

### Option A: Using Django Shell (Recommended)

1. **Open Django Shell**:
```bash
python manage.py shell
```

2. **Run these commands**:
```python
from users.models import CustomUser

# Find your user (replace 'yourusername' with your actual username)
user = CustomUser.objects.get(username='yourusername')

# Make user staff
user.is_staff = True
user.save()

# Optional: Make user superuser (full permissions)
user.is_superuser = True
user.save()

# Verify
print(f"User: {user.username}")
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")

# Exit shell
exit()
```

### Option B: Using Django Admin Interface

1. **First, create a superuser** (using Method 1 above)
2. **Login to Django Admin**: Go to `http://localhost:8000/admin/`
3. **Navigate to Users**: Click on "Users" → "Custom users"
4. **Find your user**: Click on the username
5. **Check the boxes**:
   - ✅ **Staff status** (`is_staff`)
   - ✅ **Superuser status** (`is_superuser`) - optional
6. **Save**

---

## How to Login as Admin

### Step 1: Access Admin Login Page

There are two ways to access the admin login:

**Option A: Direct URL**
```
http://localhost:8000/users/admin-login/
```

**Option B: From Navigation** (if you're already logged in as staff)
- Look for the "Admin" link in the navigation bar (only visible to staff users)

### Step 2: Enter Credentials

- **Username**: The username you created (e.g., `admin`)
- **Password**: The password you set

### Step 3: Access Dashboard

After successful login, you'll be redirected to:
```
http://localhost:8000/users/admin-dashboard/
```

---

## Quick Reference

### Create Superuser
```bash
python manage.py createsuperuser
```

### Make Existing User Staff (Django Shell)
```bash
python manage.py shell
```
```python
from users.models import CustomUser
user = CustomUser.objects.get(username='yourusername')
user.is_staff = True
user.is_superuser = True  # Optional
user.save()
exit()
```

### Admin Login URL
```
http://localhost:8000/users/admin-login/
```

### Admin Dashboard URL
```
http://localhost:8000/users/admin-dashboard/
```

### Django Admin URL (for superusers)
```
http://localhost:8000/admin/
```

---

## Troubleshooting

### "Access denied. This page is for administrators only."

**Problem**: The user you're trying to login with is not staff.

**Solution**: 
1. Make sure the user has `is_staff=True` or `is_superuser=True`
2. Use Django shell to check and update:
```python
from users.models import CustomUser
user = CustomUser.objects.get(username='yourusername')
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")
```

### "No user found with that username"

**Problem**: The username doesn't exist.

**Solution**: 
1. Create a new superuser: `python manage.py createsuperuser`
2. Or check existing users:
```python
from users.models import CustomUser
users = CustomUser.objects.all()
for user in users:
    print(user.username)
```

### Can't see "Admin" link in navigation

**Problem**: You're not logged in as a staff user.

**Solution**: 
1. Make sure you're logged in
2. Make sure your user has `is_staff=True`
3. Refresh the page

### Forgot admin password

**Solution**: Reset password using Django shell:
```python
from users.models import CustomUser
user = CustomUser.objects.get(username='admin')
user.set_password('newpassword')
user.save()
```

---

## Security Notes

⚠️ **Important Security Tips**:

1. **Use Strong Passwords**: Admin accounts have full access - use strong, unique passwords
2. **Limit Admin Users**: Only create admin accounts for trusted users
3. **Change Default Admin Username**: Don't use obvious usernames like `admin` or `administrator`
4. **Enable 2FA** (if available): Add two-factor authentication for extra security
5. **Regular Audits**: Periodically review who has admin access

---

## Admin Dashboard Features

Once logged in, you'll have access to:

- **Bug Reports Management**: View, filter, and resolve bug reports
- **User Statistics**: See total users, active users, user type breakdown
- **Resume Statistics**: View total resumes, recent resumes
- **System Health**: Check database status and system health
- **Bug Details**: View detailed bug reports with screenshots

---

## Next Steps

After creating your admin account:

1. ✅ Login at `/users/admin-login/`
2. ✅ Explore the admin dashboard
3. ✅ Review bug reports (if any)
4. ✅ Check user statistics
5. ✅ Monitor system health

---

**Last Updated**: 2025

