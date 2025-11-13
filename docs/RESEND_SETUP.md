# Resend Email Setup Guide

This guide explains how to set up Resend for sending emails on Railway.

## Why Resend?

- ✅ **Works on Railway** - Uses HTTPS API (not SMTP), so Railway doesn't block it
- ✅ **Easy Setup** - Just need an API key
- ✅ **Free Tier** - 100 emails/day free
- ✅ **Modern API** - Fast, reliable, and easy to use
- ✅ **Great Deliverability** - Professional email service

## Setup Steps

### 1. Create Resend Account

1. Go to [https://resend.com/](https://resend.com/)
2. Sign up for a free account
3. Verify your email address

### 2. Get API Key

1. Go to [https://resend.com/api-keys](https://resend.com/api-keys)
2. Click "Create API Key"
3. Give it a name (e.g., "Railway Production")
4. Copy the API key (you'll only see it once!)

### 3. Configure Railway

1. Go to your Railway project
2. Click on "Variables" tab
3. Add a new variable:
   - **Name**: `RESEND_API_KEY`
   - **Value**: Your API key from step 2
4. Click "Add"

### 4. Configure From Email (Optional)

By default, emails will be sent from `noreply@ai-resume-builder.com`.

To change this, add another Railway variable:
- **Name**: `DEFAULT_FROM_EMAIL`
- **Value**: Your preferred email address (e.g., `noreply@yourdomain.com`)

**Note**: You can use any email address, but for better deliverability, you can verify your domain in Resend.

### 5. Verify Domain (Optional - Recommended)

For better email deliverability:

1. Go to [https://resend.com/domains](https://resend.com/domains)
2. Click "Add Domain"
3. Enter your domain (e.g., `yourdomain.com`)
4. Add the DNS records Resend provides to your domain's DNS settings
5. Wait for verification (usually takes a few minutes)

Once verified, update `DEFAULT_FROM_EMAIL` to use your domain:
- `DEFAULT_FROM_EMAIL=noreply@yourdomain.com`

## Railway Environment Variables

After setup, you should have these variables in Railway:

```
RESEND_API_KEY=re_your_api_key_here
DEFAULT_FROM_EMAIL=noreply@ai-resume-builder.com  # Optional
```

## Testing

After deploying, test the email functionality:

1. Go to the password reset page
2. Enter an email address
3. Check Railway logs for any errors
4. Check your email inbox (and spam folder)

## Free Tier Limits

- **100 emails/day** (free tier)
- More than enough for most applications
- Upgrade if you need more

## Troubleshooting

### Emails not sending?

1. Check Railway logs for error messages
2. Verify `RESEND_API_KEY` is set correctly in Railway
3. Make sure the API key is active in Resend dashboard
4. Check your Resend dashboard for delivery logs

### "Invalid API key" error?

- Make sure the API key is copied correctly (no extra spaces)
- Verify the API key is active in Resend dashboard
- Try creating a new API key

### Emails going to spam?

- Verify your domain in Resend (recommended)
- Use a professional "from" email address
- Avoid spam trigger words in email content

## More Information

- Resend Dashboard: https://resend.com/overview
- Resend Documentation: https://resend.com/docs
- Resend API Reference: https://resend.com/docs/api-reference

