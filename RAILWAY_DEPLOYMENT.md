# Railway Deployment Guide

## Quick Fix for `/app/venv/bin/python: not found` Error

This error occurs when Railway's Nixpacks detects the `venv/` folder and tries to use it. The fix is to ensure `venv/` is excluded from deployment.

## Solution

### 1. Ensure `.dockerignore` or `.gitignore` Excludes venv

The `venv/` folder should NOT be committed to git. Make sure your `.gitignore` includes:

```
venv/
env/
.venv/
```

### 2. Railway Configuration

Railway will use the `nixpacks.toml` or `Procfile` to build and run your app. The configuration files are already set up:

- **`nixpacks.toml`** - Tells Nixpacks how to build (uses system Python, not venv)
- **`Procfile`** - Tells Railway how to start the app
- **`railway.json`** - Railway-specific configuration

### 3. Environment Variables in Railway Dashboard

Set these in your Railway project settings:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=tuliamvppwa-production.up.railway.app,*.railway.app
CSRF_TRUSTED_ORIGINS=https://tuliamvppwa-production.up.railway.app
N8N_LESSON_WEBHOOK_URL=
N8N_COACH_WEBHOOK_URL=
N8N_MILESTONE_WEBHOOK_URL=
N8N_ELIGIBILITY_WEBHOOK_URL=
```

### 4. Build Command Override (if needed)

If Railway still tries to use venv, you can override the build command in Railway dashboard:

**Settings → Build → Build Command:**
```
pip install --no-cache-dir -r requirements.txt
```

**Settings → Deploy → Start Command:**
```
python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT
```

### 5. Verify `.gitignore` Excludes venv

Make sure your `.gitignore` includes:
```
venv/
env/
.venv/
```

Then commit the change:
```bash
git add .gitignore
git commit -m "Ensure venv is ignored"
git push
```

## Common Issues

### Issue: Still seeing venv error
**Solution**: Delete the `venv/` folder from your repository if it was accidentally committed:
```bash
git rm -r --cached venv/
git commit -m "Remove venv from git"
git push
```

### Issue: Static files not loading
**Solution**: Railway will run `collectstatic` automatically. If issues persist, check:
- `STATIC_ROOT` is set in settings.py
- `STATIC_URL` is set correctly
- WhiteNoise is installed (already in requirements.txt)

### Issue: Database migrations not running
**Solution**: The Procfile includes `python manage.py migrate`, but if using PostgreSQL, make sure `DATABASE_URL` is set in Railway environment variables.

## Production Checklist

- [ ] `DEBUG=False` in Railway environment variables
- [ ] `SECRET_KEY` set in Railway environment variables
- [ ] `ALLOWED_HOSTS` includes your Railway domain
- [ ] `CSRF_TRUSTED_ORIGINS` includes your Railway domain
- [ ] `venv/` is NOT in git (check `.gitignore`)
- [ ] Static files are being collected (check build logs)
- [ ] Database migrations are running (check deploy logs)

## Testing Locally Before Deploy

```bash
# Test with Railway's environment
export PORT=8000
python manage.py migrate
python manage.py runserver 0.0.0.0:$PORT
```

## Need Help?

If you're still seeing the venv error:
1. Check Railway build logs for exact error message
2. Verify `venv/` is not in your git repository
3. Try clearing Railway's build cache (Settings → Deploy → Clear Build Cache)
4. Redeploy after pushing the fixes

