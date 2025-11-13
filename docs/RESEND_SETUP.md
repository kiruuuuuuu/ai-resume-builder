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

If you do want to verify a custom domain you own, follow these detailed steps:

#### Step-by-Step Domain Verification Guide

##### Step 1: Add Domain in Resend

1. Go to [https://resend.com/domains](https://resend.com/domains)
2. Click **"+ Add Domain"** button
3. Enter **ONLY your domain name** (e.g., `yourdomain.com`)
   - ❌ **Don't enter**: `https://yourdomain.com`
   - ❌ **Don't enter**: `www.yourdomain.com` (unless you want to verify www subdomain separately)
   - ✅ **Enter**: Just `yourdomain.com`
4. Select a region closest to your users (e.g., "Tokyo" for Asia, "US East" for Americas)
5. Click **"Add Domain"**

##### Step 2: Get DNS Records from Resend

After adding the domain, Resend will show you DNS records you need to add. You'll typically see:

1. **SPF Record** (Sender Policy Framework - for email authentication)
   - Type: `TXT`
   - Name/Host: `@` or `yourdomain.com` (depends on your DNS provider)
   - Value: Something like `v=spf1 include:resend.com ~all`

2. **DKIM Record** (DomainKeys Identified Mail - for email signing)
   - Type: `TXT`
   - Name/Host: Usually something like `resend._domainkey` or `default._domainkey`
   - Value: A long string provided by Resend (contains `p=` parameter)

3. **DMARC Record** (optional but recommended for better deliverability)
   - Type: `TXT`
   - Name/Host: `_dmarc`
   - Value: Something like `v=DMARC1; p=quarantine; pct=100`

**Important**: Resend will show you the exact records with specific values - **copy these exactly as shown**. Each domain gets unique DNS record values.

##### Step 3: Add DNS Records to Your Domain Provider

You need to add these DNS records where you manage your domain's DNS (usually where you bought the domain):

**Where to find DNS settings:**
- Your domain registrar (GoDaddy, Namecheap, Google Domains, etc.)
- Or your DNS provider (Cloudflare, Route 53, etc.)

**Steps for most DNS providers:**

1. **Log in to your domain registrar** or DNS provider
2. **Go to DNS Settings** (may be called "DNS Management", "DNS Records", "DNS Configuration", or "Advanced DNS")
3. **Find your domain** and click on it
4. **Add each DNS record** one by one:
   - Click "Add Record" or "Create Record" or "+ Add"
   - Select **Type**: `TXT` (for SPF, DKIM, and DMARC)
   - Enter **Name/Host**: Copy exactly from Resend
     - For root domain: Usually `@` or `yourdomain.com`
     - For DKIM: Usually `resend._domainkey` or `default._domainkey`
     - For DMARC: Usually `_dmarc`
   - Enter **Value/Content**: Copy exactly from Resend
   - Set **TTL**: `3600` (or use default/automatic)
   - Click "Save" or "Add Record"

5. **Repeat** for each DNS record Resend shows you

**Note**: Different DNS providers use different field names:
- **Name** = **Host** = **Hostname** = **Record Name**
- **Value** = **Content** = **Record Content** = **Text**
- **TTL** = Time to Live (use 3600 or default)

##### Step 4: Wait for DNS Propagation and Verification

1. **Return to Resend dashboard** → [Domains](https://resend.com/domains)
2. **Click on your domain** to see verification status
3. **DNS propagation can take**:
   - Usually: 15-30 minutes
   - Sometimes: Up to 48 hours (rare)
   - Most often: Within 1 hour
4. Resend will automatically verify once DNS records are detected
5. **Status will change** from "Pending" or "Not Verified" to "Verified" ✅

**Tip**: You can check if your DNS records are visible using:
- https://www.whatsmydns.net/ (enter your domain and select TXT records)
- https://dnschecker.org/ (check DNS propagation globally)
- https://dns.google/query?name=_dmarc.yourdomain.com&type=TXT (check specific record)

##### Step 5: Update Email Settings

Once your domain is verified:

1. **Update Railway variable** `DEFAULT_FROM_EMAIL`:
   - Go to Railway → Your Project → Variables
   - Update or add: `DEFAULT_FROM_EMAIL`
   - Value: `noreply@yourdomain.com` (replace with your verified domain)
   - Click "Add" or "Update"

2. **Redeploy** - Railway will automatically redeploy with the new from email

3. **Test** - Send a password reset email to verify it works

#### Examples for Common DNS Providers

**Cloudflare**:
1. Log in → Select your domain → DNS → Records
2. Click "Add record"
3. Type: `TXT`, Name: (from Resend), Content: (from Resend), TTL: Auto
4. Click "Save"

**GoDaddy**:
1. Log in → My Products → DNS Management
2. Click "Add" in DNS Records section
3. Type: `TXT`, Name: (from Resend), Value: (from Resend), TTL: 600
4. Click "Save"

**Namecheap**:
1. Log in → Domain List → Manage → Advanced DNS
2. Add new record
3. Type: `TXT Record`, Host: (from Resend), Value: (from Resend), TTL: Automatic
4. Click save icon (✓)

**Google Domains**:
1. Log in → DNS → Custom resource records
2. Click "Add record"
3. Type: `TXT`, Name: (from Resend), Data: (from Resend), TTL: 3600
4. Click "Add"

**AWS Route 53**:
1. Log in → Route 53 → Hosted zones → Your domain
2. Create record
3. Record type: `TXT`, Name: (from Resend), Value: (from Resend), TTL: 300
4. Create record

#### Troubleshooting Domain Verification

**Domain still not verified after 30 minutes?**

1. **Check DNS records are correct**:
   - Use [whatsmydns.net](https://www.whatsmydns.net/) to verify records are visible
   - Make sure there are no typos
   - Verify TTL is set (not blank)

2. **Common issues**:
   - ❌ DNS records have typos
   - ❌ Missing DNS records (didn't add all required records)
   - ❌ TTL not set
   - ❌ DNS provider auto-appending domain name (check if records show correctly)

3. **Remove and re-add domain**:
   - Delete the domain in Resend
   - Re-add it and copy the DNS records again
   - Add DNS records to your domain provider

4. **Check Resend dashboard**:
   - Click on your domain in Resend
   - See which records are verified (✓) and which are not (✗)
   - Add missing records

5. **Contact support**:
   - If still not working after 48 hours, contact Resend support
   - They can help verify DNS records are correct

**"Domain already exists" error?**
- The domain might already be verified in another Resend account
- Contact Resend support if you own the domain

**DNS records not showing up globally?**
- DNS propagation can take up to 48 hours (rarely)
- Check with [dnschecker.org](https://dnschecker.org/) to see propagation status
- Wait a bit longer if records are being propagated

Once verified, update `DEFAULT_FROM_EMAIL` to use your domain:
- `DEFAULT_FROM_EMAIL=noreply@yourdomain.com`

## Railway Environment Variables

**Minimum Required** (emails will work with just this):

```
RESEND_API_KEY=re_your_api_key_here
```

**Optional** (for custom from email):

```
DEFAULT_FROM_EMAIL=onboarding@resend.dev  # Default - works without verification
# OR if you verified a custom domain:
DEFAULT_FROM_EMAIL=noreply@yourdomain.com  # Requires domain verification
```

**Note**: 
- `onboarding@resend.dev` works immediately without domain verification (default)
- Custom domain emails (e.g., `noreply@yourdomain.com`) require domain verification

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

