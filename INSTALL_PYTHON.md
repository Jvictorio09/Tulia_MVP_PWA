# Fix Python Installation for Speakopoly

## Problem
The current Python installation is just Windows Store shortcuts, not actual Python.

## Solutions

### Option 1: Install Python from python.org (Recommended)

1. **Download Python 3.8+**
   - Go to https://www.python.org/downloads/
   - Download Python 3.11 or 3.12 (latest stable)
   - Choose "Windows installer (64-bit)"

2. **Install Python**
   - Run the installer as Administrator
   - ✅ **IMPORTANT**: Check "Add Python to PATH"
   - ✅ **IMPORTANT**: Check "Install for all users"
   - Choose "Customize installation"
   - ✅ Check "pip" and "tcl/tk and IDLE"
   - ✅ Check "py launcher"
   - Click "Install"

3. **Verify Installation**
   ```powershell
   python --version
   pip --version
   ```

### Option 2: Use Windows Package Manager (winget)

```powershell
# Install Python
winget install Python.Python.3.11

# Verify installation
python --version
```

### Option 3: Use Anaconda/Miniconda

1. **Download Miniconda**
   - Go to https://docs.conda.io/en/latest/miniconda.html
   - Download Windows installer

2. **Install and Setup**
   ```powershell
   # After installation, open Anaconda Prompt
   conda create -n speakopoly python=3.11
   conda activate speakopoly
   ```

## After Python Installation

### 1. Create Virtual Environment
```powershell
cd myProject
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Django Commands
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_content
python manage.py runserver
```

## Alternative: Use Docker (No Python Installation Needed)

If you prefer not to install Python locally:

### 1. Install Docker Desktop
- Download from https://www.docker.com/products/docker-desktop/
- Install and restart

### 2. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 3. Run with Docker
```powershell
docker build -t speakopoly .
docker run -p 8000:8000 speakopoly
```

## Quick Test Without Installation

You can also test the app structure using the demo files:

1. **Open `demo.html`** in your browser to see the interface
2. **Run `demo_app.py`** (if you have Python working) to see the data structure
3. **Read `README_SETUP.md`** for complete setup instructions

## Troubleshooting

### If Python Still Not Found
```powershell
# Check PATH environment variable
$env:PATH -split ';' | Where-Object { $_ -like '*python*' }

# Add Python to PATH manually
$env:PATH += ";C:\Python311;C:\Python311\Scripts"
```

### If pip Not Found
```powershell
# Install pip manually
python -m ensurepip --upgrade
```

### If Virtual Environment Issues
```powershell
# Use full path to Python
C:\Python311\python.exe -m venv venv
venv\Scripts\activate
```

## Next Steps

Once Python is properly installed:

1. **Activate virtual environment**: `venv\Scripts\activate`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run migrations**: `python manage.py makemigrations && python manage.py migrate`
4. **Seed content**: `python manage.py seed_content`
5. **Start server**: `python manage.py runserver`
6. **Open browser**: http://localhost:8000

The app will be fully functional with all features working!
