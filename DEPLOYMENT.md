# 🚀 Deployment Guide - AI Resume Builder

This guide provides step-by-step instructions for deploying the AI Resume Builder application to production.

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL 12+ (recommended for production)
- Redis 6+ (for Celery background tasks)
- Domain name (optional but recommended)
- SSL certificate (for HTTPS)
- Google AI API Key (for Gemini features)
- Server with at least 2GB RAM and 2 CPU cores

## 🔧 Step 1: Server Setup

### 1.1 Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Python and Dependencies

```bash
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx git -y
```

### 1.3 Install System Dependencies for WeasyPrint

```bash
sudo apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y
```

## 🗄️ Step 2: Database Setup

### 2.1 Create PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE ai_resume_builder;
CREATE USER ai_resume_user WITH PASSWORD 'your_secure_password';
ALTER ROLE ai_resume_user SET client_encoding TO 'utf8';
ALTER ROLE ai_resume_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_resume_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_resume_builder TO ai_resume_user;
\q
```

### 2.2 Configure PostgreSQL

Edit `/etc/postgresql/*/main/postgresql.conf`:
```
listen_addresses = 'localhost'
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 🔴 Step 3: Redis Setup

### 3.1 Configure Redis

Edit `/etc/redis/redis.conf`:
```
bind 127.0.0.1
protected-mode yes
```

### 3.2 Start Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 📦 Step 4: Application Deployment

### 4.1 Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/kiruuuuuuu/ai-resume-builder.git
sudo chown -R $USER:$USER ai-resume-builder
cd ai-resume-builder
```

### 4.2 Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

**Required Environment Variables:**

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
USE_POSTGRESQL=True

# Database
DB_NAME=ai_resume_builder
DB_USER=ai_resume_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Google AI
GOOGLE_AI_API_KEY=your-google-ai-api-key
USE_GEMINI=True
GEMINI_MODEL=models/gemini-2.5-flash

# Celery/Redis
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Age Validation
MIN_AGE=18
MAX_AGE=100

# Optional: AWS S3 for Media Files
USE_S3=False
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=us-east-1

# Optional: Social Authentication
# GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
# GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
# GITHUB_CLIENT_ID=your-github-client-id
# GITHUB_CLIENT_SECRET=your-github-client-secret
```

**Generate Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.5 Run Migrations

```bash
python manage.py migrate
```

### 4.6 Create Superuser

```bash
python manage.py createsuperuser
```

### 4.7 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4.8 Test Application

```bash
python manage.py runserver 0.0.0.0:8000
```

Visit `http://your-server-ip:8000` to verify it's working.

## 🔄 Step 5: Celery Setup

### 5.1 Create Celery Service File

```bash
sudo nano /etc/systemd/system/celery.service
```

**Content:**

```ini
[Unit]
Description=Celery Service for AI Resume Builder
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-resume-builder
Environment="PATH=/var/www/ai-resume-builder/venv/bin"
ExecStart=/var/www/ai-resume-builder/venv/bin/celery -A core worker --loglevel=info --logfile=/var/log/celery/worker.log --pidfile=/var/run/celery/worker.pid --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.2 Create Directories

```bash
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown -R www-data:www-data /var/log/celery /var/run/celery
```

### 5.3 Start Celery

```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
```

## 🌐 Step 6: Nginx Configuration

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/ai-resume-builder
```

**Content:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    # For initial setup, use HTTP:
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/ai-resume-builder/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/ai-resume-builder/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    client_max_body_size 10M;
}
```

### 6.2 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/ai-resume-builder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🚀 Step 7: Gunicorn Setup

### 7.1 Install Gunicorn

```bash
pip install gunicorn
```

### 7.2 Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Content:**

```ini
[Unit]
Description=Gunicorn daemon for AI Resume Builder
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-resume-builder
Environment="PATH=/var/www/ai-resume-builder/venv/bin"
ExecStart=/var/www/ai-resume-builder/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/ai-resume-builder/gunicorn.sock \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    core.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 7.3 Update Nginx for Gunicorn

Edit `/etc/nginx/sites-available/ai-resume-builder`:

```nginx
location / {
    proxy_pass http://unix:/var/www/ai-resume-builder/gunicorn.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 7.4 Create Log Directory

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn
```

### 7.5 Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 🔒 Step 8: SSL Certificate (Let's Encrypt)

### 8.1 Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 8.2 Obtain Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 8.3 Auto-Renewal

```bash
sudo certbot renew --dry-run
```

## 📝 Step 9: Final Configuration

### 9.1 Set Proper Permissions

```bash
sudo chown -R www-data:www-data /var/www/ai-resume-builder
sudo chmod -R 755 /var/www/ai-resume-builder
sudo chmod -R 775 /var/www/ai-resume-builder/media
```

### 9.2 Update ALLOWED_HOSTS

Ensure your domain is in `ALLOWED_HOSTS` in `.env`:
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 9.3 Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart nginx
```

## 🔍 Step 10: Verify Deployment

1. **Check Services Status:**
   ```bash
   sudo systemctl status gunicorn
   sudo systemctl status celery
   sudo systemctl status nginx
   ```

2. **Test Application:**
   - Visit `https://yourdomain.com`
   - Test user registration
   - Test resume creation
   - Test PDF generation

3. **Check Logs:**
   ```bash
   sudo tail -f /var/log/gunicorn/error.log
   sudo tail -f /var/log/celery/worker.log
   sudo tail -f /var/log/nginx/error.log
   ```

## 🔄 Step 11: Deployment Updates

### 11.1 Update Application

```bash
cd /var/www/ai-resume-builder
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

## 📊 Step 12: Monitoring & Maintenance

### 12.1 Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/ai-resume-builder
```

**Content:**
```
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn > /dev/null 2>&1 || true
    endscript
}
```

### 12.2 Monitor Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep -E 'gunicorn|celery|nginx'
```

## 🐳 Alternative: Docker Deployment

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_resume_builder
      POSTGRES_USER: ai_resume_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - USE_POSTGRESQL=True
      - DB_HOST=db
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery:
    build: .
    command: celery -A core worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - USE_POSTGRESQL=True
      - DB_HOST=db
      - CELERY_BROKER_URL=redis://redis:6379/0

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## 🌍 Platform-Specific Guides

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn core.wsgi:application
   worker: celery -A core worker --loglevel=info
   ```
3. Deploy:
   ```bash
   heroku create
   heroku addons:create heroku-postgresql
   heroku addons:create heroku-redis
   git push heroku main
   ```

### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings
3. Add PostgreSQL and Redis databases
4. Set environment variables
5. Deploy

### AWS Elastic Beanstalk

1. Install EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create`
4. Deploy: `eb deploy`

## ⚠️ Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY`
- [ ] Secure database passwords
- [ ] HTTPS enabled (SSL certificate)
- [ ] `ALLOWED_HOSTS` configured
- [ ] Firewall configured (UFW)
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Environment variables secured
- [ ] Media files access restricted

## 🆘 Troubleshooting

### Application Not Loading
- Check Gunicorn status: `sudo systemctl status gunicorn`
- Check logs: `sudo tail -f /var/log/gunicorn/error.log`
- Verify database connection
- Check Redis connection

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check Nginx static file configuration
- Verify file permissions

### Celery Not Working
- Check Redis: `redis-cli ping`
- Check Celery status: `sudo systemctl status celery`
- Check logs: `sudo tail -f /var/log/celery/worker.log`

### 502 Bad Gateway
- Check Gunicorn socket permissions
- Verify Nginx proxy configuration
- Check Gunicorn is running

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Need Help?** Open an issue on [GitHub](https://github.com/kiruuuuuuu/ai-resume-builder/issues)

