# Using Gmail API for Email on Railway

Railway blocks direct SMTP connections to Gmail, but you CAN still use Gmail by using the Gmail API instead of SMTP. The Gmail API uses HTTPS, which Railway allows.

## Prerequisites

1. A Google Cloud Project with Gmail API enabled
2. OAuth 2.0 credentials for your Gmail account
3. Service account credentials or OAuth tokens

## Setup Steps

### 1. Enable Gmail API in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the **Gmail API**
4. Create OAuth 2.0 credentials (if using OAuth) or Service Account (if using service account)

### 2. Install Required Package

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Add to `requirements.txt`:
```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

### 3. Configure Django Settings

Set these environment variables in Railway:

```
EMAIL_BACKEND=core.email_backends.GmailAPIBackend
GMAIL_API_USER=your-email@gmail.com
GMAIL_API_CREDENTIALS_FILE=path/to/credentials.json  # Or use GMAIL_API_CREDENTIALS_JSON (base64 encoded)
GMAIL_API_TOKEN_FILE=path/to/token.json  # Will be created automatically
```

### 4. Create Custom Email Backend

You'll need to create a custom Django email backend that uses Gmail API. This is more complex than SMTP but works on Railway.

## Alternative: Use a Service That Works

While Gmail API works, it's more complex. Consider these alternatives that work seamlessly with Railway:

### Recommended: SendGrid (Free Tier: 100 emails/day)
- Simple SMTP setup
- Better deliverability
- Email analytics
- Free tier available

### Other Options:
- **Resend**: Modern API, great for developers
- **Mailgun**: Reliable, good free tier
- **Postmark**: Excellent deliverability

## Comparison

| Method | Railway Support | Setup Complexity | Cost |
|--------|----------------|------------------|------|
| Gmail SMTP | ❌ Blocked | Easy | Free |
| Gmail API | ✅ Works | Complex | Free |
| SendGrid | ✅ Works | Easy | Free (100/day) |
| Resend | ✅ Works | Easy | Free (100/day) |

## Recommendation

If you want to stick with Gmail, we can implement Gmail API support. However, SendGrid or Resend are easier to set up and provide better deliverability and analytics.

