# Railway Build Fix - Django Not Installing

## Problem
Railway isn't installing Django from `requirements.txt` during build.

## Solution

### Option 1: Set Build Command in Railway Dashboard (Recommended)

1. Go to Railway Dashboard → Your Project → Settings → Build
2. Set **Build Command** to:
   ```
   pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
3. Leave **Start Command** empty (Procfile will be used)

### Option 2: Check Railway Service Settings

In Railway Dashboard:
- **Settings → Build → Build Command**: Should be empty OR set to `pip install -r requirements.txt`
- **Settings → Deploy → Start Command**: Should be empty (uses Procfile)

### Option 3: Verify requirements.txt is in Root

Make sure `requirements.txt` is in the root directory (`myProject/requirements.txt`), not in a subdirectory.

### Option 4: Clear Build Cache

1. Railway Dashboard → Settings
2. Scroll to "Build Cache"
3. Click "Clear Build Cache"
4. Redeploy

### Option 5: Check Build Logs

In Railway Dashboard → Deployments → Latest Deployment → View Logs

Look for:
- ✅ "Detected Python project"
- ✅ "Installing dependencies from requirements.txt"
- ✅ "Successfully installed Django-5.1.1"
- ❌ If you see "No requirements.txt found", the file isn't being detected

## Quick Fix Commands

If Railway still isn't installing, manually set in Railway Dashboard:

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
python manage.py migrate && gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT
```

## Verify Files

Make sure these are committed:
- ✅ `requirements.txt` (root directory)
- ✅ `Procfile` (root directory)
- ✅ `manage.py` (root directory)
- ✅ `runtime.txt` (optional, but helpful)

## Test Locally First

Before deploying, test that requirements.txt works:
```bash
pip install -r requirements.txt
python manage.py --version  # Should show Django version
```

