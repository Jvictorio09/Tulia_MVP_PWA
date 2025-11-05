# Docker Setup for Tulia

## Quick Start

### 1. Build the Docker Image
```bash
docker build -t tulia-app .
```

### 2. Run the Container
```bash
docker run -p 8000:8000 tulia-app
```

Or use docker-compose:
```bash
docker-compose up
```

## Common Issues Fixed

### Issue: `/app/venv/bin/python: not found`
**Solution**: The Dockerfile now installs Python packages directly (no venv needed in Docker containers).

### Issue: Build context too large
**Solution**: `.dockerignore` excludes `venv/`, `__pycache__/`, and other unnecessary files.

## Production Setup

For production, update the Dockerfile CMD to use gunicorn:

```dockerfile
CMD gunicorn myProject.wsgi:application --bind 0.0.0.0:8000
```

## Environment Variables

Create a `.env` file (not committed to git):

```env
SECRET_KEY=your-secret-key-here
DEBUG=0
ALLOWED_HOSTS=tuliamvppwa-production.up.railway.app,localhost
N8N_LESSON_WEBHOOK_URL=
N8N_COACH_WEBHOOK_URL=
N8N_MILESTONE_WEBHOOK_URL=
N8N_ELIGIBILITY_WEBHOOK_URL=
```

## Build and Deploy

```bash
# Build
docker build -t tulia-app .

# Test locally
docker run -p 8000:8000 -e DEBUG=1 tulia-app

# For Railway/Render/other platforms
# Push to container registry and deploy
```

