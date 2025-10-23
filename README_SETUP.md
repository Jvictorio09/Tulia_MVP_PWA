# Speakopoly - Educational Communication App

A Duolingo-like micro-lessons app for high-stakes communication with streaks, quests, level gates, and "city/district" progression.

## Features Implemented

### ✅ Core Models & Database Structure
- **User Management**: Extended profiles with learning preferences and progress tracking
- **Educational Content**: 6 levels with units, lessons, and exercises
- **Exercise Types**: Select, match, rewrite, listen, speak, scenario, milestone
- **Gamification**: Streaks, quests, rewards, leaderboards, districts
- **Subscriptions**: Free, Super, and Super Family tiers
- **Content Management**: Rich content blocks and tip sheets

### ✅ Backend Architecture
- **Django + DRF**: RESTful API for mobile/web
- **Authentication**: Social login (Google, Apple, Facebook) via django-allauth
- **Background Tasks**: Celery for async processing
- **Caching**: Redis for performance
- **Media Storage**: AWS S3 integration ready
- **Payments**: Stripe integration for subscriptions

### ✅ Frontend Framework
- **Django Templates**: Server-side rendering
- **HTMX**: Progressive interactivity without React/Vue
- **Alpine.js**: Lightweight state management
- **TailwindCSS**: Modern, responsive UI
- **Audio Recording**: Browser MediaRecorder API

### ✅ Educational Content (Level 1)
- **Awareness & Foundations** (75 minutes total)
- **4 Units**: High-Stakes Context, Audience Psychology, Clarity vs Jargon, Building Presence
- **12+ Exercises**: Multiple choice, matching, rewriting, audio practice
- **Milestone Challenge**: 30-second introduction recording
- **3 Districts**: Amphitheater, Forum, Market with themed coaches

## Setup Instructions

### Prerequisites
1. **Python 3.8+** installed
2. **Redis** server running
3. **PostgreSQL** (or SQLite for development)

### Installation

1. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_content  # Seed Level 1 content
python manage.py createsuperuser
```

4. **Run Development Server**
```bash
python manage.py runserver
```

5. **Access the App**
- Web App: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API: http://localhost:8000/api/

## Key Features

### 🏠 Home Page (Speakopoly City)
- Interactive city map with districts
- Level progression visualization
- Active quests and streak display
- Quick action buttons

### 📚 Lesson Runner
- Interactive exercise interface
- Real-time progress tracking
- Audio recording capabilities
- Immediate feedback and scoring

### 🎯 Exercise Types
1. **Select**: Multiple choice questions
2. **Match**: Drag-and-drop ordering
3. **Rewrite**: Text clarity improvement
4. **Listen**: Audio comprehension
5. **Speak**: Voice recording practice
6. **Scenario**: Branching dialogue choices
7. **Milestone**: Extended recording challenges

### 🏆 Gamification System
- **Streaks**: Daily learning streaks with fire emoji
- **Quests**: Daily, weekly, and special challenges
- **Rewards**: Coins, gems, badges, and tokens
- **Leaderboards**: Competitive rankings
- **Districts**: Unlockable venues with themed coaches

### 💰 Subscription Tiers
- **Free**: Level 1 access, basic features
- **Super**: All levels, AI feedback, no ads
- **Super Family**: Family sharing, parental controls

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/signup/` - User registration
- `POST /accounts/logout/` - User logout

### Lessons
- `GET /lesson/{id}/` - Lesson runner interface
- `POST /exercise/{id}/submit/` - Submit exercise attempt
- `GET /milestone/{id}/` - Milestone challenge
- `POST /milestone/{id}/submit/` - Submit milestone attempt

### Gamification
- `GET /streak/` - User streak page
- `GET /leaderboard/` - Leaderboard rankings
- `GET /quests/` - Active quests

## Content Structure

### Level 1: Awareness & Foundations
- **Unit 1**: High-Stakes Context (15 min)
  - What Makes Communication High-Stakes?
  - Stakes Assessment Framework
  - Practice: Stakes Identification
- **Unit 2**: Audience Psychology (20 min)
- **Unit 3**: Clarity vs Jargon (20 min)
- **Unit 4**: Building Presence (20 min)

### Districts & Coaches
- **Amphitheater**: Marcus Aurelius (Presence & Authority)
- **Forum**: Cicero (Persuasive Communication)
- **Market**: Athena (Strategic Communication)

## Development Notes

### HTMX Integration
- Progressive enhancement without full SPA
- Real-time exercise submission
- Dynamic content updates
- Form handling without page reloads

### Audio Processing
- Browser MediaRecorder API
- Audio upload to Django
- Speech-to-text integration ready
- Rubric-based scoring system

### Scoring Algorithm
- Exercise-specific scoring logic
- Streak multipliers (up to 2x)
- Partial credit for attempts
- Milestone rubric evaluation

## Next Steps

1. **Install Python and dependencies**
2. **Run migrations and seed content**
3. **Test the lesson runner interface**
4. **Implement remaining levels (2-6)**
5. **Add AI/ML speech scoring**
6. **Deploy to production**

## Production Deployment

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_live_...
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
OPENAI_API_KEY=your-openai-key
```

### Recommended Stack
- **Web Server**: Nginx + Gunicorn
- **Database**: PostgreSQL
- **Cache**: Redis
- **Media Storage**: AWS S3
- **Background Tasks**: Celery + Redis
- **Monitoring**: Sentry

This implementation provides a solid foundation for a Duolingo-like educational app with all the core features you specified. The modular design allows for easy expansion to additional levels and features.
