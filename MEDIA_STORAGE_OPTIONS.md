# Media Storage Options for Photos

## 📸 What Files Need Storage?

Your application stores:
1. **Profile Photos** - User profile pictures
2. **Company Logos** - Employer company logos  
3. **Bug Report Screenshots** - Screenshots from bug reports
4. **Generated PDFs** - Resume PDF files (optional, can be regenerated)

---

## ✅ Do You Need Cloud Storage?

### Short Answer: **NO, Not Required!**

You have **TWO options**:

### Option 1: Fly Volumes (FREE) ⭐ **Recommended for Start**

- ✅ **FREE** - No additional cost
- ✅ **Simple** - Easy to set up
- ✅ **Persistent** - Files survive deployments
- ✅ **Good for starting** - Perfect for small to medium apps
- ⚠️ **Limited** - Not shared across regions
- ⚠️ **Backup** - You need to handle backups manually

### Option 2: AWS S3 (PAID) ⭐ **Recommended for Production**

- ✅ **Scalable** - Handles unlimited files
- ✅ **Reliable** - High availability
- ✅ **Backup** - Built-in backup options
- ✅ **CDN** - Can use CloudFront for fast delivery
- ⚠️ **Costs money** - Pay per GB stored and transferred
- ⚠️ **Setup required** - Need AWS account and configuration

---

## 🎯 Recommendation

### For Starting Out: Use Fly Volumes (FREE)

**Why?**
- Free to use
- Easy setup (2 commands)
- Perfect for testing and small apps
- No AWS account needed
- Can switch to S3 later

### For Production/Scale: Use AWS S3

**Why?**
- Better for large scale
- Better performance with CDN
- Better backup options
- Industry standard

**But**: You can start with Fly Volumes and switch to S3 later!

---

## 🚀 Quick Setup Guide

### Option 1: Fly Volumes (FREE) - Recommended

#### Step 1: Create Volume

```bash
fly volumes create media_data --size 3 --region iad
```

**Size**: 3GB is usually enough to start (you can increase later)
**Region**: Use the same region as your app (e.g., `iad` for US East)

#### Step 2: Update fly.toml

Add this to your `fly.toml`:

```toml
[[mounts]]
  source = "media_data"
  destination = "/app/media"
```

#### Step 3: That's It! ✅

Your app will automatically use `/app/media` for storing files.

**No additional configuration needed!** The app already supports this.

---

### Option 2: AWS S3 (PAID)

#### Step 1: Create AWS Account

1. Go to https://aws.amazon.com
2. Sign up (requires credit card, but has free tier)
3. Navigate to S3 Console

#### Step 2: Create S3 Bucket

1. Click "Create bucket"
2. Name: `ai-resume-builder-media` (or your choice)
3. Region: Choose closest to your users
4. **Uncheck** "Block all public access" (or configure CORS properly)
5. Click "Create bucket"

#### Step 3: Create IAM User

1. Go to IAM Console
2. Click "Users" → "Add users"
3. Username: `ai-resume-builder-s3-user`
4. **Access type**: Programmatic access
5. **Permissions**: Attach policy `AmazonS3FullAccess` (or create custom policy)
6. Click "Create user"
7. **Save Access Key ID and Secret Access Key** (you'll need these)

#### Step 4: Configure CORS (Optional but Recommended)

In S3 bucket → Permissions → CORS:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
        "AllowedOrigins": ["https://yourapp.fly.dev"],
        "ExposeHeaders": ["ETag"]
    }
]
```

#### Step 5: Set Environment Variables

```bash
fly secrets set \
  USE_S3=True \
  AWS_ACCESS_KEY_ID="your-access-key-id" \
  AWS_SECRET_ACCESS_KEY="your-secret-access-key" \
  AWS_STORAGE_BUCKET_NAME="ai-resume-builder-media" \
  AWS_S3_REGION_NAME="us-east-1"
```

#### Step 6: That's It! ✅

The app will automatically use S3 when `USE_S3=True`.

---

## 💰 Cost Comparison

### Fly Volumes
- **Cost**: FREE (included in Fly.io)
- **Storage**: 3GB (default, can increase)
- **Limits**: Volume size limits

### AWS S3
- **Cost**: ~$0.023 per GB/month (storage)
- **Cost**: ~$0.09 per GB (data transfer out)
- **Free Tier**: 5GB storage, 20,000 GET requests for 12 months
- **Example**: 10GB storage = ~$0.23/month + transfer costs

**For small apps**: Fly Volumes is essentially free
**For large apps**: S3 is worth the cost for reliability

---

## 📋 Quick Decision Guide

### Choose Fly Volumes If:
- ✅ You're just starting out
- ✅ You want to keep costs low (FREE)
- ✅ You have < 10GB of files
- ✅ You don't need multi-region storage
- ✅ You want simple setup

### Choose AWS S3 If:
- ✅ You expect lots of files (> 10GB)
- ✅ You need high availability
- ✅ You want CDN integration
- ✅ You need automatic backups
- ✅ You want industry-standard storage

---

## 🔄 Switching Later

**Good News**: You can switch from Fly Volumes to S3 anytime!

**Steps**:
1. Set up S3 (follow Option 2 above)
2. Set `USE_S3=True` in Fly.io secrets
3. Migrate files (optional - new uploads will go to S3)
4. Deploy

**Old files**: Will remain on Fly Volume (can migrate manually if needed)
**New files**: Will go to S3

---

## ✅ Recommendation for You

### Start with Fly Volumes (FREE)

**Why?**
1. ✅ **FREE** - No additional costs
2. ✅ **Simple** - Just 2 commands
3. ✅ **Enough** - 3GB is plenty for starting
4. ✅ **Flexible** - Can switch to S3 later

**Setup Time**: 5 minutes

**Commands**:
```bash
# 1. Create volume
fly volumes create media_data --size 3 --region iad

# 2. Add to fly.toml (add this section)
[[mounts]]
  source = "media_data"
  destination = "/app/media"
```

**That's it!** Your photos will be stored on the Fly volume.

---

## 📝 Summary

### Do You Need Cloud Storage?

**Answer**: **NO, not required!**

**Options**:
1. **Fly Volumes** (FREE) - Recommended for starting
2. **AWS S3** (PAID) - Recommended for production/scale

**Recommendation**: 
- **Start with Fly Volumes** (free, simple)
- **Switch to S3 later** if needed (easy to switch)

**Setup**: 
- Fly Volumes: 2 commands (5 minutes)
- AWS S3: 15-20 minutes + AWS account

---

## 🎯 Next Steps

### If Using Fly Volumes (Recommended):
1. Create volume: `fly volumes create media_data --size 3 --region iad`
2. Add mount to `fly.toml`
3. Deploy - Done! ✅

### If Using AWS S3:
1. Create AWS account
2. Create S3 bucket
3. Create IAM user
4. Set environment variables
5. Deploy - Done! ✅

---

**Bottom Line**: Start with Fly Volumes (FREE), switch to S3 later if needed!

