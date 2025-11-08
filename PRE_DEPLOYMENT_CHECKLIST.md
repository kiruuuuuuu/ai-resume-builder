# Pre-Deployment Checklist

Use this checklist to ensure your AI Resume Builder application is ready for production deployment on Fly.io.

## 🔒 Security Checklist

### Critical Security Settings
- [ ] **SECRET_KEY**: Set a strong, unique secret key in environment variables
  - Generate using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - Never commit to version control
  - Set in Fly.io secrets: `fly secrets set DJANGO_SECRET_KEY="your-secret-key"`

- [ ] **DEBUG**: Set to `False` in production
  - Set in Fly.io secrets: `fly secrets set DEBUG=False`
  - Verify: `DEBUG=False` in `.env` or environment variables

- [ ] **ALLOWED_HOSTS**: Configure with your domain(s)
  - Set in Fly.io secrets: `fly secrets set ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"`
  - Include Fly.io app URL: `fly secrets set ALLOWED_HOSTS="yourdomain.com,yourapp.fly.dev"`

- [ ] **CSRF_TRUSTED_ORIGINS**: Add your domain(s) if using custom domain
  - Add to `core/settings.py`: `CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com', 'https://yourapp.fly.dev']`

### Security Headers
- [ ] Verify security middleware is enabled in `MIDDLEWARE`
- [ ] Consider adding security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- [ ] Ensure HTTPS is enforced (automatic on Fly.io with custom domains)

## 📦 Environment Variables

### Required Environment Variables
Set all of these in Fly.io using `fly secrets set`:

- [ ] `DJANGO_SECRET_KEY` - Django secret key (CRITICAL)
- [ ] `DEBUG=False` - Disable debug mode
- [ ] `ALLOWED_HOSTS` - Comma-separated list of allowed domains
- [ ] `GOOGLE_AI_API_KEY` - Google Gemini API key
- [ ] `USE_GEMINI=True` - Enable Gemini features (or False to disable)
- [ ] `GEMINI_MODEL` - Gemini model (default: `models/gemini-2.5-flash`)

### Database Configuration
- [ ] `USE_POSTGRESQL=True` - Enable PostgreSQL
- [ ] `DB_NAME` - Database name
- [ ] `DB_USER` - Database user
- [ ] `DB_PASSWORD` - Database password
- [ ] `DB_HOST` - Database host (from Fly Postgres)
- [ ] `DB_PORT` - Database port (usually 5432)

### Celery/Redis Configuration
- [ ] `CELERY_BROKER_URL` - Redis connection URL (from Fly Redis or external)
- [ ] `CELERY_RESULT_BACKEND` - Redis connection URL for results

### Optional Environment Variables
- [ ] `JOBS_FEATURE_ENABLED` - Set to `True` to enable job features (default: `False`)
- [ ] `DJANGO_LOG_LEVEL` - Logging level (default: `INFO`)
- [ ] AWS S3 credentials (if using S3 for media files):
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
  - `AWS_S3_REGION_NAME`

## 🗄️ Database

- [ ] **Migrations**: Run all migrations
  ```bash
  python manage.py migrate
  ```

- [ ] **Database Backup**: Create backup of development database (if needed)
- [ ] **PostgreSQL Setup**: Fly Postgres database created and configured
- [ ] **Connection Test**: Verify database connection works
- [ ] **Superuser**: Create admin superuser
  ```bash
  python manage.py createsuperuser
  ```

## 📁 Static Files

- [ ] **Collect Static Files**: Run collectstatic
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **WhiteNoise**: Verify WhiteNoise is configured in `MIDDLEWARE`
- [ ] **STATIC_ROOT**: Verify path is correct
- [ ] **STATIC_URL**: Verify URL is correct

## 📸 Media Files

- [ ] **Storage Strategy**: Decide on storage (Fly volumes or AWS S3)
- [ ] **AWS S3 Setup** (if using):
  - [ ] S3 bucket created
  - [ ] IAM user with proper permissions
  - [ ] CORS configuration set
  - [ ] Environment variables configured
- [ ] **Fly Volumes** (if using local storage):
  - [ ] Volume created: `fly volumes create media_data`
  - [ ] Volume mounted in `fly.toml`

## 🔄 Celery & Redis

- [ ] **Redis Setup**: Fly Redis or external Redis configured
- [ ] **Celery Worker**: Worker process configured in `fly.toml`
- [ ] **Task Testing**: Test Celery tasks work correctly
- [ ] **Worker Logs**: Verify worker logs are accessible

## ✅ Application Health

- [ ] **All Tests Pass**: Run test suite
  ```bash
  python manage.py test
  ```

- [ ] **No Linter Errors**: Check for code quality issues
- [ ] **Dependencies**: All packages in `requirements.txt` are compatible
- [ ] **Python Version**: Verify Python 3.11+ compatibility

## 📝 Documentation

- [ ] **README.md**: Updated with current information
- [ ] **DEPLOYMENT_GUIDE.md**: Complete deployment instructions
- [ ] **REMAINING_WORK.md**: Documented known issues and improvements

## 🚀 Deployment-Specific

### Fly.io Specific
- [ ] **Fly CLI**: Installed and authenticated
- [ ] **fly.toml**: Configuration file created and configured
- [ ] **App Created**: Fly.io app initialized
- [ ] **PostgreSQL**: Fly Postgres database attached
- [ ] **Redis**: Fly Redis or external Redis configured
- [ ] **Secrets**: All environment variables set via `fly secrets set`
- [ ] **Health Checks**: Health check endpoint configured
- [ ] **Processes**: Web server and Celery worker processes configured

## 🔍 Pre-Launch Testing

- [ ] **Local Testing**: Application runs correctly locally
- [ ] **Database Migration**: Test migrations on production database
- [ ] **Static Files**: Verify static files load correctly
- [ ] **Media Files**: Test file uploads/downloads
- [ ] **User Registration**: Test user signup flow
- [ ] **Resume Creation**: Test resume builder functionality
- [ ] **PDF Generation**: Test PDF download
- [ ] **AI Features**: Test Gemini AI integration
- [ ] **Admin Dashboard**: Test admin login and dashboard
- [ ] **Bug Reports**: Test bug reporting functionality

## 📊 Monitoring & Logging

- [ ] **Error Logging**: Configure error logging
- [ ] **Application Logs**: Verify logs are accessible via `fly logs`
- [ ] **Database Monitoring**: Set up database monitoring (optional)
- [ ] **Uptime Monitoring**: Set up uptime monitoring (optional)

## 🔐 Backup Strategy

- [ ] **Database Backups**: Configure automatic backups (Fly Postgres has built-in backups)
- [ ] **Media Backups**: Plan for media file backups (if using local storage)
- [ ] **Backup Testing**: Test backup restoration process

## ✅ Final Checks

- [ ] **Domain Configuration**: Custom domain configured (if applicable)
- [ ] **SSL Certificate**: SSL automatically configured by Fly.io
- [ ] **Performance**: Test application performance
- [ ] **Security Scan**: Run security checks
- [ ] **Load Testing**: Basic load testing (optional but recommended)

---

## Quick Command Reference

```bash
# Set all secrets at once
fly secrets set DJANGO_SECRET_KEY="..." DEBUG=False ALLOWED_HOSTS="..." GOOGLE_AI_API_KEY="..."

# Check secrets
fly secrets list

# View logs
fly logs

# Check app status
fly status

# SSH into app
fly ssh console
```

---

**Note**: This checklist should be completed before deploying to production. Mark each item as you complete it.

