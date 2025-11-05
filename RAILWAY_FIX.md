# Railway Deployment Fix

## The Problem
Railway isn't installing Django and other dependencies from `requirements.txt`.

## Solution

### 1. Check Railway Build Settings

In Railway Dashboard:
- Go to your project → **Settings** → **Build**
- Make sure **Build Command** is empty (Railway should auto-detect)
- Or set it to: `pip install -r requirements.txt`

### 2. Verify Files Are Committed

Make sure these files are in your git repository:
- `requirements.txt` (with all dependencies)
- `Procfile` (with gunicorn command)
- `runtime.txt` (Python version)
- `manage.py` (in root directory)

### 3. Check Railway Service Settings

In Railway Dashboard:
- Go to your service → **Settings** → **Deploy**
- **Start Command** should be: `gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT`
- Or leave empty to use Procfile

### 4. Manual Build Command (if auto-detect fails)

If Railway still doesn't install dependencies, set in Railway Dashboard:

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
python manage.py migrate && gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT
```

### 5. Check Build Logs

In Railway Dashboard → **Deployments** → Click on latest deployment → **View Logs**

Look for:
- ✅ `Installing requirements from requirements.txt`
- ✅ `Successfully installed Django-5.1.1`
- ❌ If you see errors installing packages, check the logs

### 6. Common Issues

**Issue: Python version mismatch**
- Solution: `runtime.txt` specifies Python 3.11.9

**Issue: Dependencies not installing**
- Solution: Check `requirements.txt` is in root directory
- Make sure no syntax errors in requirements.txt

**Issue: Build cache problems**
- Solution: In Railway Dashboard → Settings → Clear Build Cache → Redeploy

## Quick Test

After deploying, check Railway logs. You should see:
1. Python detected
2. Installing from requirements.txt
3. Django installed successfully
4. Gunicorn starting

If you still see "Django not found", check that `requirements.txt` is being read during build.

