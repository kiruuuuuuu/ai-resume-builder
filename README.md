AI Resume Builder — Development README
This README provides comprehensive step-by-step instructions to set up and run this Django project on a Windows machine. It covers two setup methods: using Conda (recommended for easier PDF generation) and using a standard Python venv.

The project uses Celery and Redis for asynchronous background tasks.

Links
Miniconda (Conda Installer): https://docs.conda.io/en/latest/miniconda.html

Redis for Windows (direct download): https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip

Setup Instructions
Follow either the recommended Conda method or the alternative venv method.

Method 1: Recommended Setup (with Conda)
This method is highly recommended as it simplifies the installation of WeasyPrint and its dependencies, which are required for generating PDF resumes.

Install Miniconda: If you don't have it, download and install it from the link above.

Create and Activate Conda Environment:

# Create a new environment named 'resume_env' with Python 3.11
conda create -n resume_env python=3.11 -y

# Activate the environment
conda activate resume_env

Install WeasyPrint:

# Install WeasyPrint and its native dependencies from the conda-forge channel
conda install -c conda-forge weasyprint -y

Install Python Dependencies & Set Up Database:

# Navigate to your project directory
cd path\to\your\AI_Resume_Builder

# Install all required packages
pip install -r requirements.txt

# Create the database schema
python manage.py migrate

Method 2: Alternative Setup (with venv)
Use this method if you prefer not to use Conda. Note that PDF generation may fail unless you manually install the required GTK dependencies for WeasyPrint.

Create and Activate Virtual Environment:

# Navigate to your project directory
cd path\to\your\AI_Resume_Builder

# Create a virtual environment named 'resume_env'
python -m venv resume_env

# Activate the environment
.\resume_env\Scripts\Activate.ps1

Install Dependencies & Set Up Database:

# Install all required packages
pip install -r requirements.txt

# Create the database schema
python manage.py migrate

Running the Application
After completing either setup method, you need to run three services in three separate terminals.

Terminal 1: Start the Redis Server
Redis is our message broker for background tasks.

Download and extract Redis from the link provided at the top of this README.

Open a terminal, navigate to the extracted folder, and run the server.

# Example navigation
cd C:\Redis-x64-3.0.504

# Run the server

.\redis-server.exe

Leave this terminal running.

Terminal 2: Start the Celery Worker
This worker process handles the background AI tasks.

Open a new terminal and navigate to your project root.

Activate your environment (conda activate resume_env or .\resume_env\Scripts\Activate.ps1).

Start the Celery worker.

# The -P eventlet flag is required for Celery on Windows
celery -A core worker -l info -P eventlet

Leave this terminal running.

Terminal 3: Start the Django Server
This is your main web application.

Open a third terminal and navigate to your project root.

Activate your environment.

Start the Django server.

python manage.py runserver

Access the Application
With all three terminals running, you can access the AI Resume Builder in your web browser at:

http://127.0.0.1:8000/