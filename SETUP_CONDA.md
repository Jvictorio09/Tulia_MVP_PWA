# Setup Speakopoly with Conda

Since you have Python in conda, here are the steps to get the Django app running:

## Option 1: If Conda is Installed but Not in PATH

### Find Conda Installation
```powershell
# Check common conda locations
Get-ChildItem -Path "C:\Users\$env:USERNAME\" -Name "*conda*" -Directory -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\ProgramData\" -Name "*conda*" -Directory -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\" -Name "*conda*" -Directory -ErrorAction SilentlyContinue
```

### Initialize Conda for PowerShell
```powershell
# If you find conda, initialize it for PowerShell
C:\Users\$env:USERNAME\anaconda3\Scripts\conda.exe init powershell
# OR
C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe init powershell

# Restart PowerShell after initialization
```

## Option 2: Use Anaconda Prompt

1. **Open Anaconda Prompt** (search in Start Menu)
2. **Navigate to project**:
   ```bash
   cd "E:\New Downloads\Tulia\myProject"
   ```

3. **Create conda environment**:
   ```bash
   conda create -n speakopoly python=3.11
   conda activate speakopoly
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Django commands**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_content
   python manage.py runserver
   ```

## Option 3: Direct Python Path

If you know where conda Python is installed:

```powershell
# Example paths (adjust based on your installation)
C:\Users\$env:USERNAME\anaconda3\python.exe -m venv venv
C:\Users\$env:USERNAME\miniconda3\python.exe -m venv venv

# Activate and install
venv\Scripts\activate
pip install -r requirements.txt
```

## Option 4: Use Anaconda Navigator

1. **Open Anaconda Navigator**
2. **Go to Environments tab**
3. **Create new environment**:
   - Name: `speakopoly`
   - Python version: 3.11
4. **Install packages**:
   - Click on environment
   - Go to "Not Installed"
   - Search and install: `django`, `djangorestframework`, `django-allauth`, etc.

## Quick Test

Let's test if we can find and use conda Python:

```powershell
# Try to find Python in conda directories
Get-ChildItem -Path "C:\Users\$env:USERNAME\" -Name "python.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_ -like "*conda*" -or $_ -like "*anaconda*" }
```

## Alternative: Use the Demo

If conda setup is complex, you can still test the app:

1. **Open `demo.html`** in your browser to see the interface
2. **Check `README_SETUP.md`** for complete setup instructions
3. **Use the demo files** to understand the app structure

## Troubleshooting

### If conda command not found:
```powershell
# Add conda to PATH temporarily
$env:PATH += ";C:\Users\$env:USERNAME\anaconda3\Scripts"
$env:PATH += ";C:\Users\$env:USERNAME\miniconda3\Scripts"
```

### If Python not found in conda:
```powershell
# Check conda environments
conda env list
conda activate base
python --version
```

### If pip not working:
```powershell
# Update conda first
conda update conda
conda install pip
```

## Next Steps

Once you have conda working:

1. **Create environment**: `conda create -n speakopoly python=3.11`
2. **Activate**: `conda activate speakopoly`
3. **Install**: `pip install -r requirements.txt`
4. **Run**: `python manage.py runserver`

The app will be fully functional with all the educational features!
