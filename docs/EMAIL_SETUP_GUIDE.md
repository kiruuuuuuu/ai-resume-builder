# Email Setup Guide for Password Reset

This guide will help you configure email functionality for password reset in production.

## Step 1: Enable 2-Factor Authentication on Gmail

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under **Signing in to Google**, find **2-Step Verification**
4. Click on it and follow the prompts to enable 2-factor authentication
   - You'll need to verify your phone number
   - You may need to enter a verification code sent to your phone

## Step 2: Generate an App Password

1. After enabling 2-Step Verification, go back to **Security** settings
2. Under **Signing in to Google**, you should now see **App passwords**
3. Click on **App passwords**
   - If you don't see this option, make sure 2-Step Verification is fully enabled
4. You may need to sign in again
5. Select **Mail** as the app type
6. Select **Other (Custom name)** as the device type
7. Enter a name like "AI Resume Builder Production" or "Railway App"
8. Click **Generate**
9. **IMPORTANT**: Copy the 16-character password that appears (it will look like: `abcd efgh ijkl mnop`)
   - You won't be able to see it again!
   - Remove the spaces when using it (it should be: `abcdefghijklmnop`)

## Step 3: Configure Email Variables in Railway

Use the Railway CLI or Dashboard to set these variables:

### Using Railway CLI (Recommended)

```bash
# Set email backend to SMTP
railway variables --set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Set email host (Gmail SMTP)
railway variables --set EMAIL_HOST=smtp.gmail.com

# Set email port
railway variables --set EMAIL_PORT=587

# Enable TLS
railway variables --set EMAIL_USE_TLS=True

# Disable SSL (TLS and SSL are different)
railway variables --set EMAIL_USE_SSL=False

# Set your Gmail address
railway variables --set EMAIL_HOST_USER=your-email@gmail.com

# Set the App Password (the 16-character password from Step 2, no spaces)
railway variables --set EMAIL_HOST_PASSWORD=abcdefghijklmnop

# Set the from email address
railway variables --set DEFAULT_FROM_EMAIL=noreply@ai-resume-builder.com

# Set server email (usually same as DEFAULT_FROM_EMAIL)
railway variables --set SERVER_EMAIL=noreply@ai-resume-builder.com
```

### Using Railway Dashboard

1. Go to https://railway.app
2. Select your project → **ai-resume-builder** service
3. Go to the **Variables** tab
4. Click **New Variable** for each variable below:

| Variable Name | Value |
|--------------|-------|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_USE_SSL` | `False` |
| `EMAIL_HOST_USER` | `your-email@gmail.com` (your actual Gmail address) |
| `EMAIL_HOST_PASSWORD` | `your-16-char-app-password` (the App Password from Step 2) |
| `DEFAULT_FROM_EMAIL` | `noreply@ai-resume-builder.com` |
| `SERVER_EMAIL` | `noreply@ai-resume-builder.com` |

## Step 4: Verify Configuration

1. Railway will automatically redeploy after adding variables
2. Wait for deployment to complete (check the Deployments tab)
3. Test the password reset functionality:
   - Go to your login page
   - Click "Forgot password?"
   - Enter a registered email address
   - Check the email inbox for the reset link

## Troubleshooting

### "Invalid credentials" error
- Make sure you're using the **App Password**, not your regular Gmail password
- Verify the App Password has no spaces
- Ensure 2-Step Verification is enabled

### "Connection refused" or "Timeout" error
- Check that `EMAIL_PORT=587` and `EMAIL_USE_TLS=True`
- Verify `EMAIL_USE_SSL=False` (TLS and SSL are different)

### Emails not received
- Check spam/junk folder
- Verify the email address is registered in your system
- Check Railway logs for email sending errors
- Make sure `EMAIL_HOST_USER` is your full Gmail address

### "Less secure app access" error
- This shouldn't happen with App Passwords
- If you see this, make sure you're using an App Password, not your regular password

## Alternative: Using Other Email Providers

### SendGrid
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

### Mailgun
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailgun-username
EMAIL_HOST_PASSWORD=your-mailgun-password
```

### AWS SES
```bash
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

## Security Notes

- **Never commit App Passwords to version control**
- App Passwords are safer than regular passwords
- You can revoke App Passwords anytime from Google Account settings
- Use different App Passwords for different applications

