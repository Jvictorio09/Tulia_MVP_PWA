# Fix Railway 502 - Development Server Issue

## Problem
Your Railway logs show:
```
Starting development server at http://0.0.0.0:8000/
```

This means Railway is running `python manage.py runserver` instead of Gunicorn. The development server is **not production-ready** and causes 502 errors.

## Solution: Set Start Command in Railway Dashboard

### Step 1: Go to Railway Dashboard
1. Open your Railway project
2. Click on your service (Tulia_MVP_PWA)
3. Go to **Settings** tab (top right)

### Step 2: Set Start Command
1. Scroll down to **Deploy** section
2. Find **Start Command** field
3. **Delete any existing command** (especially if it says `python manage.py runserver`)
4. Set it to:
   ```
   python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn myProject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
   ```
5. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **Redeploy** or push a new commit
3. Wait for deployment to complete

### Step 4: Verify
Check the **Deploy Logs** - you should now see:
- ✅ "Starting gunicorn"
- ✅ "Booting worker"
- ✅ "Listening at: http://0.0.0.0:XXXX"

NOT:
- ❌ "Starting development server" (this is wrong)

## Alternative: Verify Procfile is Being Used

If Railway isn't reading your Procfile:
1. Make sure `Procfile` is in the root directory (same level as `manage.py`)
2. Make sure it's committed to git
3. In Railway Settings → Deploy → Start Command, leave it **empty** (Railway will use Procfile)

## Why This Happens

Railway's auto-detection sometimes picks up Django and tries to run it with `runserver`. The development server:
- Can only handle one request at a time
- Isn't designed for production
- Times out easily
- Causes 502 errors

Gunicorn is production-ready with multiple workers.

