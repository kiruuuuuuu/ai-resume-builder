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
   - **Value**: Your API key from step 2 (e.g., `re_xxxxx...`)
4. Click "Add"

**That's it!** You can now send emails. Domain verification is NOT required.

### 4. Configure From Email (Optional)

By default, emails will be sent from `noreply@ai-resume-builder.com`.

To change this, add another Railway variable:
- **Name**: `DEFAULT_FROM_EMAIL`
- **Value**: Your preferred email address (e.g., `noreply@yourdomain.com`)

**Important**: On Resend's free tier, you can send from ANY email address without domain verification. Domain verification is optional and only needed if you want:
- Better deliverability (slightly)
- To send from a custom domain you own
- More professional email addresses

### 5. Verify Domain (Optional - Only if you own a custom domain)

**⚠️ IMPORTANT**: You don't need to verify a domain to use Resend! You can skip this step.

Domain verification is only needed if:
- You own a custom domain (e.g., `yourdomain.com`)
- You want to send from `noreply@yourdomain.com` for better deliverability
- You want a more professional email address

**DO NOT** try to verify Railway subdomains like `ai-resume-builder-jk.up.railway.app` - these are not your domains and cannot be verified.

If you do want to verify a custom domain you own:

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
- **Can send from any email address** (no domain verification needed!)
- More than enough for most applications
- Upgrade if you need more

## Common Mistakes

### ❌ Don't Enter Railway Subdomain in Resend
- **Wrong**: `https://ai-resume-builder-jk.up.railway.app/`
- **Wrong**: `ai-resume-builder-jk.up.railway.app`
- **Why**: You don't own Railway subdomains, so you can't verify them in Resend

### ✅ You Don't Need Domain Verification!
- You can send emails immediately with just the API key
- Resend free tier allows sending from any email address
- Domain verification is only for custom domains you own

### ✅ What to Enter in Domain Field (Only if You Own a Domain)
- **Correct**: `yourdomain.com` (just the domain, no `https://`, no paths)
- **Example**: If you own `example.com`, enter `example.com`

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

