# Fix 502 Error - Development Server Issue

## Problem
Railway is running `python manage.py runserver` (development server) instead of Gunicorn. The development server is single-threaded and not suitable for production, causing 502 errors.

## Solution

### Option 1: Set Start Command in Railway Dashboard (FASTEST)

1. Go to Railway Dashboard → Your Project → Settings → Deploy
2. Set **Start Command** to:
   ```
   python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
   ```
3. Save and redeploy

### Option 2: Verify Procfile is Being Used

The `Procfile` should have:
```
web: python manage.py migrate --noinput; python manage.py collectstatic --noinput; gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
```

### Option 3: Use railway.json (Already Updated)

The `railway.json` now explicitly sets the start command. This should override Railway's auto-detection.

## Why Development Server Causes 502

- Single-threaded (can't handle multiple requests)
- Not production-ready
- Times out easily
- No worker processes

Gunicorn is production-ready with multiple workers.

## After Fixing

Check logs - you should see:
- ✅ "Starting gunicorn"
- ✅ "Booting worker"
- ✅ "Listening at: http://0.0.0.0:XXXX"

NOT:
- ❌ "Starting development server" (this is wrong)

## Quick Check

In Railway Dashboard → Settings → Deploy → Start Command:
- Should be empty (uses Procfile) OR set to the Gunicorn command above
- Should NOT be `python manage.py runserver`

