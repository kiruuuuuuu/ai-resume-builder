# 🤖 AI Resume Builder v2.0

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/kiruuuuuuu/ai-resume-builder?style=social)](https://github.com/kiruuuuuuu/ai-resume-builder)

**An intelligent resume creation platform powered by AI** that helps job seekers build professional resumes with real-time feedback, scoring, and job matching. Built with Django, Celery, Redis, and Google Gemini AI.

[Features](#-features) • [Installation](#-installation) • [Deployment](#-deployment) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

## 🚀 Features

- **AI-Powered Resume Builder**: Create professional resumes with multiple templates (Classic, Modern, Professional, Creative)
- **Real-time AI Feedback**: Get instant scoring and actionable suggestions to improve your resume
- **Job Matching**: Intelligent matching between resumes and job postings using AI
- **Interview Preparation**: AI-generated interview questions tailored to your resume and job requirements
- **Multiple Resume Templates**: Choose from 4 professionally designed templates with customizable color schemes
- **PDF Export**: Generate high-quality PDF resumes for download
- **User Authentication**: Secure login/registration with optional social authentication (Google, GitHub)
- **Job Application Tracking**: Track your applications with detailed status updates
- **Employer Dashboard**: Employers can post jobs and manage applications

## 📋 Prerequisites

- Python 3.11+
- Redis (for Celery background tasks)
- PostgreSQL (for production) or SQLite (for development)
- Google AI API Key (for Gemini features)

## 🛠️ Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kiruuuuuuu/ai-resume-builder.git
   cd ai-resume-builder
   ```

2. **Set up environment**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # - Set DJANGO_SECRET_KEY
   # - Set GOOGLE_AI_API_KEY
   # - Configure database settings
   ```

3. **Install dependencies** (see detailed setup below)

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

### Detailed Setup Instructions

For comprehensive setup instructions including Conda installation, WeasyPrint setup, and Redis configuration, please refer to the [Complete Documentation](docs/DOCUMENTATION.md).

#### Method 1: Recommended Setup (with Conda)

This method is highly recommended as it simplifies the installation of WeasyPrint and its dependencies.

1. **Install Miniconda**: Download from [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

2. **Create and activate environment**:
   ```bash
   conda create -n resume_env python=3.11 -y
   conda activate resume_env
   ```

3. **Install WeasyPrint**:
   ```bash
   conda install -c conda-forge weasyprint -y
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

#### Method 2: Alternative Setup (with venv)

```bash
python -m venv resume_env
source resume_env/bin/activate  # Windows: resume_env\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Running the Application

You need to run three services in separate terminals:

### Terminal 1: Redis Server

**Windows**:
```bash
# Download Redis from: https://github.com/microsoftarchive/redis/releases
cd C:\Redis-x64-3.0.504
.\redis-server.exe
```

**Linux/Mac**:
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
# or
brew install redis  # macOS

# Start Redis
redis-server
# or
sudo systemctl start redis  # Linux
```

### Terminal 2: Celery Worker

**Windows (Development)**:
```bash
celery -A core worker -l info -P solo
```

**Linux/Mac (Production)**:
```bash
pip install eventlet
celery -A core worker -l info -P eventlet --concurrency=50
```

### Terminal 3: Django Server

```bash
python manage.py runserver
```

### Access the Application

Open your browser and navigate to:
- **http://127.0.0.1:8000/**

## 🚀 Deployment

For production deployment instructions, see:
- **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)** - ⭐ **Recommended: FREE tier, no payment method required**
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Fly.io deployment guide (requires payment method)
- **[PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[SECURITY_FIXES_GUIDE.md](SECURITY_FIXES_GUIDE.md)** - Security fixes and improvements

### 🎯 Quick Recommendation

**For Free Deployment (No Payment Method)**:
- Use **[Railway.app](RAILWAY_DEPLOYMENT_GUIDE.md)** - FREE tier, no credit card required, includes PostgreSQL and Redis

**For Fly.io**:
- Requires payment method (even for free tier)
- You get $5 free credit
- Won't be charged if you stay within limits

## 📚 Documentation

### Main Documentation Files

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Comprehensive setup, configuration, and feature guides
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete Fly.io deployment guide with step-by-step instructions
- **[PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist and status
- **[SECURITY_FIXES_GUIDE.md](SECURITY_FIXES_GUIDE.md)** - Security fixes, improvements, and checklist
- **[ADMIN_SETUP_GUIDE.md](ADMIN_SETUP_GUIDE.md)** - How to create admin user and access admin dashboard
- **[TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md)** - How to run tests and test coverage
- **[REMAINING_WORK.md](REMAINING_WORK.md)** - Remaining tasks and improvements

### Quick Links

- **Celery Configuration** - See [DOCUMENTATION.md](docs/DOCUMENTATION.md#celery-configuration)
- **Social Login Setup** - See [DOCUMENTATION.md](docs/DOCUMENTATION.md#social-login-setup)
- **Database Configuration** - See [DOCUMENTATION.md](docs/DOCUMENTATION.md#database-configuration)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

**Required**:
- `DJANGO_SECRET_KEY` - Django secret key
- `GOOGLE_AI_API_KEY` - Google AI API key for Gemini features

**Optional**:
- `DEBUG` - Set to `True` for development (default: `True`)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `USE_POSTGRESQL` - Set to `True` to use PostgreSQL (default: `False`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - PostgreSQL configuration
- `USE_S3` - Set to `True` for AWS S3 media storage (default: `False`)
- `CELERY_BROKER_URL` - Redis connection URL (default: `redis://127.0.0.1:6379/0`)

See `.env.example` for the complete list of available variables.

### Database Configuration

**Development (SQLite - Default)**:
```bash
# In .env
USE_POSTGRESQL=False
```

**Production (PostgreSQL)**:
```bash
# In .env
USE_POSTGRESQL=True
DB_NAME=ai_resume_builder
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

For detailed PostgreSQL setup, see [DOCUMENTATION.md](docs/DOCUMENTATION.md#database-configuration).

## 🎨 Features Overview

### Resume Builder

- **Multiple Templates**: Choose from Classic, Modern, Professional, and Creative templates
- **Color Customization**: Select from multiple color schemes
- **Live Preview**: Preview your resume in real-time before downloading
- **PDF Export**: Generate high-quality PDF resumes
- **AI Scoring**: Get instant feedback on your resume quality

### Job Matching

- **Intelligent Matching**: AI-powered matching between resumes and job postings
- **Match Score**: Percentage-based compatibility score
- **Application Tracking**: Track your applications with detailed status updates

### Interview Preparation

- **AI-Generated Questions**: Personalized interview questions based on your resume and job requirements
- **STAR Method Answers**: Structured answers using Situation, Task, Action, Result format
- **Practice Questions**: Practice with realistic interview scenarios

### Employer Features

- **Job Posting**: Create and manage job postings
- **Application Management**: View and manage applications
- **Interview Scheduling**: Schedule and manage interviews with applicants

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📦 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for Celery
- [ ] Set up environment variables
- [ ] Run `python manage.py collectstatic`
- [ ] Configure web server (Nginx + Gunicorn recommended)
- [ ] Set up SSL certificates
- [ ] Configure process management (systemd/supervisor)

For detailed deployment instructions, see **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**.

## 🐛 Troubleshooting

### Common Issues

**WeasyPrint PDF Generation Fails**:
- Use Conda installation method (recommended)
- Or manually install GTK dependencies for your platform

**Celery Worker Not Processing Tasks**:
- Ensure Redis is running
- Check Celery worker logs for errors
- Verify `CELERY_BROKER_URL` in settings

**Database Connection Errors**:
- Verify database credentials in `.env`
- Ensure PostgreSQL service is running (if using PostgreSQL)
- Check database user permissions

**Static Files Not Loading**:
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is configured correctly

For more troubleshooting tips, see [DOCUMENTATION.md](docs/DOCUMENTATION.md#troubleshooting).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📸 Screenshots

_Coming soon - Add screenshots of your application here!_

## 🛠️ Tech Stack

- **Backend**: Django 5.2.5, Python 3.11+
- **AI/ML**: Google Gemini AI, scikit-learn
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL (production) / SQLite (development)
- **PDF Generation**: WeasyPrint
- **Frontend**: Tailwind CSS, Django Templates
- **Authentication**: django-allauth (Google, GitHub OAuth)
- **Storage**: AWS S3 (optional) / Local storage

## 📝 License

This project is **Proprietary - All Rights Reserved**. 

**Copyright (c) 2025 Kiran**

This software is protected by copyright laws. Unauthorized copying, modification, distribution, or use of this software, via any medium is strictly prohibited without the express written permission of the copyright owner.

**Key Restrictions:**
- ❌ No copying or cloning
- ❌ No modification or derivative works
- ❌ No distribution or sublicensing
- ❌ No reverse engineering
- ❌ No commercial use without permission

For licensing inquiries, please contact: **kiruk421@gmail.com**

See the [LICENSE](LICENSE) file for full terms and conditions.

## 👨‍💻 Author

Created by Kiran

## 🙏 Acknowledgments

- Django for the excellent web framework
- Celery for background task processing
- Google Gemini AI for intelligent features
- WeasyPrint for PDF generation
- All open-source contributors

## 📞 Support

For issues or questions:
1. Check the [Documentation](docs/DOCUMENTATION.md)
2. Open an issue on the repository
3. Check existing issues for solutions

---

**Last Updated**: 2025
