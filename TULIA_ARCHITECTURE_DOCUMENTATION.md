# Tulia MVP PWA - Architecture & Logic Documentation

**Generated:** 2025-01-27  
**Version:** 1.0  
**Project:** Tulia/SpeakPro - High-Stakes Communication Learning Platform

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Overview](#architecture-overview)
4. [Database Schema & Models](#database-schema--models)
5. [URL Routing & Views](#url-routing--views)
6. [Business Logic & Core Features](#business-logic--core-features)
7. [Frontend Architecture](#frontend-architecture)
8. [Data Flow & User Journeys](#data-flow--user-journeys)
9. [External Integrations](#external-integrations)
10. [Deployment & Configuration](#deployment--configuration)

---

## Project Overview

**Tulia** (formerly SpeakPro) is a Progressive Web Application (PWA) designed to help users master high-stakes communication skills through structured micro-lessons, gamification, and AI-powered coaching.

### Key Features
- **Structured Learning Path**: 6 levels organized into units and lessons
- **Interactive Exercises**: Multiple exercise types (select, match, rewrite, listen, speak, scenario, milestone)
- **Gamification**: XP, coins, gems, streaks, leaderboards, and quests
- **AI Coach**: Webhook-integrated AI chat assistant for on-demand help
- **Milestone Challenges**: Speech recording assessments with rubric-based scoring
- **Speakopoly Theme**: City/district-based progression system
- **Subscription Management**: Support for family plans and Stripe integration

---

## Technology Stack

### Backend
- **Framework**: Django 5.1.1
- **Database**: SQLite3 (development)
- **API Framework**: Django REST Framework 3.15.2
- **Authentication**: Django's built-in authentication system
- **CORS**: django-cors-headers 4.3.1
- **Extensions**: django-extensions 3.2.3

### Frontend
- **Templating**: Django Templates
- **CSS Framework**: TailwindCSS (via CDN)
- **JavaScript Libraries**:
  - HTMX 1.9.10 (for dynamic interactions)
  - Alpine.js 3.x (for reactive components)
- **PWA Features**: Progressive Web App capabilities

### Deployment
- **Hosting**: Railway (production)
- **Server**: Gunicorn 22.0.0
- **Static Files**: WhiteNoise 6.6.0
- **Environment**: Python 3.9+

### External Services
- **AI Chat**: n8n webhook (configurable via `AI_CHAT_WEBHOOK_URL`)
- **Payments**: Stripe (configured but not fully implemented)
- **Storage**: AWS S3 (configured but not fully implemented)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
│  (Django Templates + TailwindCSS + HTMX + Alpine.js)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Django Application                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Views Layer (myApp/views.py)                        │   │
│  │  - Authentication, Lessons, Exercises, Quests, etc.  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Models Layer (myApp/models.py)                      │   │
│  │  - Profile, Level, Lesson, Exercise, etc.            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  URL Routing (myApp/urls.py)                         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ORM
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    SQLite Database                           │
│  (db.sqlite3)                                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              External Services (via HTTP)                    │
│  - n8n Webhook (AI Chat)                                    │
│  - Stripe (Payments)                                        │
│  - AWS S3 (Media Storage)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Application Structure

```
Tulia_MVP_PWA/
├── myProject/              # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
├── myApp/                  # Main application
│   ├── models.py          # Database models (18 models)
│   ├── views.py           # View functions (26 views)
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   ├── templates/         # HTML templates
│   │   └── myApp/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── lesson_runner.html
│   │       ├── ai_chat.html
│   │       ├── landing/   # Public landing page
│   │       └── auth/      # Login/signup
│   └── management/        # Custom management commands
│       └── commands/
│           └── seed_content.py
├── db.sqlite3             # SQLite database
├── insert_lesson.py       # Content seeding script
├── insert_quests.py       # Quest seeding script
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

---

## Database Schema & Models

### Model Hierarchy

The application follows a hierarchical content structure:

```
Level (1-6)
  └── Unit (multiple per level)
      └── Lesson (multiple per unit, 5-10 min each)
          └── Exercise (multiple per lesson)
              └── ExerciseAttempt (user responses)
```

### Core Models

#### 1. **Profile** (Extended User Profile)
- **Purpose**: Extends Django's User model with learning-specific data
- **Key Fields**:
  - `current_level` (1-6): User's current learning level
  - `total_xp`: Total experience points earned
  - `current_streak`: Current daily streak
  - `coins`, `gems`: Currency for rewards
  - `daily_goal_minutes`: User's learning goal
  - `learning_goal`: Learning objective string
- **Relationships**: OneToOne with User

#### 2. **Level** (Learning Levels 1-6)
- **Purpose**: Top-level learning progression containers
- **Key Fields**:
  - `number`: Level number (1-6)
  - `name`, `description`: Level information
  - `xp_required`: XP needed to unlock
  - `district_name`, `district_description`: Speakopoly theme
  - `coins_reward`, `gems_reward`: Completion rewards
- **Relationships**: Has many Units, Districts, MilestoneChallenges

#### 3. **Unit** (Units within Levels)
- **Purpose**: Groups related lessons (e.g., "Awareness & Foundations")
- **Key Fields**:
  - `name`, `description`: Unit information
  - `order`: Display order within level
  - `duration_minutes`: Estimated completion time
- **Relationships**: Belongs to Level, has many Lessons

#### 4. **Lesson** (Individual Lessons)
- **Purpose**: 5-10 minute learning sessions
- **Key Fields**:
  - `name`, `description`: Lesson information
  - `order`: Display order within unit
  - `duration_minutes`: Estimated time
  - `xp_reward`: XP awarded on completion
  - `tip_sheet`: Learning tips content
  - `learning_objectives`: Lesson goals
- **Relationships**: Belongs to Unit, has many Exercises

#### 5. **Exercise** (Interactive Exercises)
- **Purpose**: Individual practice activities within lessons
- **Exercise Types**:
  - `select`: Single/Multi-select questions
  - `match`: Match/Order exercises
  - `rewrite`: Text rewriting for clarity
  - `listen`: Tap what you hear
  - `speak`: Say it aloud
  - `scenario`: Scenario-based choices
  - `milestone`: Milestone recording
- **Key Fields**:
  - `exercise_type`: Type of exercise
  - `prompt`: Exercise question/instruction
  - `stimulus_text/audio/image`: Media content
  - `options`: JSON array of choices
  - `correct_answers`: JSON array of correct answers
  - `reference_rewrite`: Correct rewrite text
  - `rubric_criteria`: Scoring criteria (for milestones)
  - `xp_reward`: XP per exercise
  - `max_attempts`: Maximum retries allowed
  - `hints`, `feedback_correct`, `feedback_incorrect`: User guidance
- **Relationships**: Belongs to Lesson

#### 6. **ExerciseAttempt** (User Exercise Submissions)
- **Purpose**: Tracks user responses to exercises
- **Key Fields**:
  - `user_response`: JSON array of user answers
  - `audio_recording`: URL to audio (for speak/milestone)
  - `duration_seconds`: Time taken
  - `is_correct`: Boolean pass/fail
  - `score`: Float 0.0-1.0
  - `xp_earned`: XP awarded
  - `ai_feedback`: AI-generated feedback
  - `rubric_scores`: JSON dict of rubric scores
- **Relationships**: Belongs to User and Exercise

#### 7. **MilestoneChallenge** (Level Milestones)
- **Purpose**: Speech recording challenges at level completion
- **Key Fields**:
  - `name`, `description`: Challenge information
  - `duration_seconds`: Recording duration
  - `rubric`: JSON dict of scoring criteria
  - `xp_reward`, `coins_reward`: Completion rewards
- **Relationships**: Belongs to Level

#### 8. **MilestoneAttempt** (Milestone Submissions)
- **Purpose**: Tracks milestone challenge attempts
- **Key Fields**:
  - `audio_recording`: URL to recording
  - `is_passed`: Boolean pass/fail (70% threshold)
  - `overall_score`: Float 0.0-1.0
  - `rubric_scores`: JSON dict of individual criteria scores
  - `ai_feedback`: AI-generated feedback
- **Relationships**: Belongs to User and MilestoneChallenge

#### 9. **Quest** (Daily/Weekly Challenges)
- **Purpose**: Gamification quests for user engagement
- **Quest Types**: `daily`, `weekly`, `special`
- **Key Fields**:
  - `name`, `description`: Quest information
  - `xp_required`, `lessons_required`, `streak_required`: Requirements
  - `xp_reward`, `coins_reward`, `gems_reward`: Rewards
  - `is_active`: Active status
  - `expires_at`: Expiration datetime
- **Relationships**: Has many UserQuests

#### 10. **UserQuest** (User Quest Progress)
- **Purpose**: Tracks user progress on quests
- **Key Fields**:
  - `is_completed`: Completion status
  - `progress`: JSON dict tracking requirements
  - `completed_at`: Completion timestamp
- **Relationships**: Belongs to User and Quest

#### 11. **Streak** (Daily Streak Tracking)
- **Purpose**: Tracks consecutive learning days
- **Key Fields**:
  - `current_streak`: Current consecutive days
  - `longest_streak`: Best streak record
  - `last_activity`: Last activity timestamp
  - `streak_freeze_used`: Freeze mechanism flag
- **Relationships**: Belongs to User

#### 12. **LeaderboardEntry** (Competitive Rankings)
- **Purpose**: Leaderboard rankings (unlocked after N lessons)
- **Key Fields**:
  - `total_xp`: User's total XP
  - `current_streak`: Current streak
  - `lessons_completed`: Lesson count
  - `rank`: Leaderboard position
  - `league`: bronze, silver, gold, diamond
- **Relationships**: Belongs to User

#### 13. **District** (Speakopoly Districts)
- **Purpose**: Thematic districts for each level
- **Key Fields**:
  - `name`, `description`: District information
  - `image`: District image URL
  - `coach_name`, `coach_description`: District coach
  - `xp_required`: Unlock requirement
- **Relationships**: Belongs to Level

#### 14. **Reward** (Badges & Rewards)
- **Purpose**: Rewards users can earn
- **Reward Types**: `coin`, `gem`, `badge`, `token`
- **Key Fields**:
  - `name`, `description`: Reward information
  - `reward_type`: Type of reward
  - `icon`: Icon URL
  - `level_required`, `xp_required`: Unlock requirements
- **Relationships**: Has many UserRewards

#### 15. **UserReward** (Earned Rewards)
- **Purpose**: Tracks rewards earned by users
- **Key Fields**:
  - `quantity`: Number of rewards
  - `earned_at`: Earned timestamp
- **Relationships**: Belongs to User and Reward

#### 16. **SubscriptionPlan** (Subscription Tiers)
- **Purpose**: Subscription plan definitions
- **Key Fields**:
  - `name`, `description`: Plan information
  - `price_monthly`, `price_yearly`: Pricing
  - `features`: JSON array of features
  - `max_family_members`: Family plan limit
  - `stripe_price_id_monthly/yearly`: Stripe integration
- **Relationships**: Has many Subscriptions

#### 17. **Subscription** (User Subscriptions)
- **Purpose**: Active user subscriptions
- **Key Fields**:
  - `stripe_subscription_id`, `stripe_customer_id`: Stripe IDs
  - `is_active`: Active status
  - `started_at`, `expires_at`: Subscription dates
- **Relationships**: Belongs to User and SubscriptionPlan, many-to-many with User (family members)

#### 18. **ContentBlock** (CMS-like Content)
- **Purpose**: Rich content blocks for lessons/exercises
- **Key Fields**:
  - `title`, `content`: Content
  - `content_type`: text, image, video, audio
  - `order`: Display order
- **Relationships**: Belongs to Lesson or Exercise (optional)

#### 19. **AuthProvider** (Social Authentication)
- **Purpose**: Social login provider tracking
- **Key Fields**:
  - `provider`: google, apple, facebook
  - `provider_id`: Provider user ID
- **Relationships**: Belongs to User

---

## URL Routing & Views

### URL Patterns (`myApp/urls.py`)

#### Authentication Routes
- `GET/POST /login/` → `login_view()` - User login
- `GET/POST /signup/` → `signup_view()` - User registration
- `GET /logout/` → `logout_view()` - User logout
- `GET /accounts/login/` → `login_redirect()` - Login redirect handler

#### Main Application Routes
- `GET /` → `home()` - Home page (landing for non-auth, dashboard for auth)
- `GET /levels/` → `levels_view()` - All levels overview
- `GET /profile/` → `profile_view()` - User profile page
- `GET /streak/` → `streak_page()` - Streak tracking page
- `GET /leaderboard/` → `leaderboard()` - Leaderboard rankings
- `GET /quests/` → `quests()` - Quests page
- `POST /quests/<id>/start/` → `start_quest()` - Start a quest
- `POST /quests/<id>/complete/` → `complete_quest()` - Complete a quest

#### Learning Routes
- `GET /lesson/<id>/` → `lesson_runner()` - Interactive lesson page
- `GET /exercise/<id>/` → `exercise_detail()` - Individual exercise view
- `POST /exercise/<id>/submit/` → `submit_exercise()` - Submit exercise attempt
- `POST /lesson/<id>/complete/` → `complete_lesson()` - Complete lesson
- `GET /milestone/<level_id>/` → `milestone_challenge()` - Milestone challenge page
- `POST /milestone/<id>/submit/` → `submit_milestone()` - Submit milestone attempt

#### AI Chat Routes
- `GET /ai-chat/` → `ai_chat()` - AI chat interface
- `POST /ai-chat/send/` → `send_ai_message()` - Send message to AI webhook

### View Functions (`myApp/views.py`)

#### Authentication Views
1. **`login_view(request)`**
   - Handles user authentication
   - Redirects to home on success
   - Shows error messages on failure

2. **`signup_view(request)`**
   - Creates new user accounts
   - Creates associated Profile
   - Sets default learning preferences
   - Sets session flag for signup completion tracking

3. **`logout_view(request)`**
   - Logs out user
   - Redirects to home

#### Core Application Views
4. **`home(request)`**
   - **For authenticated users**: Shows dashboard with:
     - Current level and available districts
     - Active quests
     - Leaderboard position
     - Signup completion flag
   - **For non-authenticated users**: Shows landing page

5. **`lesson_runner(request, lesson_id)`**
   - Loads lesson and all exercises
   - Gets user's completed exercises
   - Tracks first lesson status
   - Renders interactive lesson interface

6. **`submit_exercise(request, exercise_id)`**
   - Processes exercise submissions (JSON)
   - Calculates score via `calculate_exercise_score()`
   - Applies streak multiplier to XP (max 2x)
   - Creates ExerciseAttempt record
   - Updates user profile (XP, coins)
   - Updates streak via `update_user_streak()`
   - Returns JSON response with feedback

7. **`calculate_exercise_score(exercise, user_response)`**
   - **select/scenario**: Compares user response to correct answers
     - Exact match: 1.0
     - Partial match: 0.5
     - No match: 0.0
   - **match**: Calculates order similarity
   - **rewrite**: Uses word overlap similarity
   - **listen/speak**: Placeholder (0.8) - production would use speech-to-text
   - Returns float 0.0-1.0

8. **`complete_lesson(request, lesson_id)`**
   - Awards lesson XP and coins
   - Unlocks next level if applicable
   - Calls `unlock_next_level()` for rewards
   - Returns JSON with next level info

9. **`milestone_challenge(request, level_id)`**
   - Loads milestone challenge for level
   - Shows user's previous attempts
   - Renders milestone recording interface

10. **`submit_milestone(request, milestone_id)`**
    - Processes milestone audio submission
    - Calculates rubric scores (placeholder - production uses AI)
    - Calculates overall score with weighted criteria
    - Pass threshold: 70%
    - Awards XP and coins
    - Unlocks next level if passed

11. **`update_user_streak(user)`**
    - Updates daily streak based on activity
    - Resets if >24 hours gap
    - Increments if exactly 1 day since last activity
    - Updates longest streak record
    - Syncs with Profile model

12. **`unlock_next_level(user)`**
    - Creates level completion rewards
    - Awards badges and coins
    - Creates UserReward records

13. **`quests(request)`**
    - Shows all active quests
    - Displays user's quest progress
    - Renders quest management interface

14. **`start_quest(request, quest_id)`**
    - Creates UserQuest record
    - Initializes progress tracking
    - Shows success/error messages

15. **`complete_quest(request, quest_id)`**
    - Marks quest as completed
    - Awards quest rewards (XP, coins, gems)
    - Updates user profile

16. **`profile_view(request)`**
    - Shows user profile
    - Displays recent activity
    - Shows earned rewards

17. **`leaderboard(request)`**
    - Shows top 50 leaderboard entries
    - Displays user's position
    - Shows league rankings

18. **`streak_page(request)`**
    - Shows streak information
    - Displays recent activity
    - Shows streak statistics

19. **`ai_chat(request)`**
    - Renders AI chat interface
    - Loads user context (level, XP, streak)

20. **`send_ai_message(request)`**
    - Sends message to n8n webhook
    - Includes user context (level, XP, streak, username)
    - Handles various response formats
    - Returns AI response to client
    - Error handling for timeouts and HTTP errors

---

## Business Logic & Core Features

### 1. **Progression System**

#### Level Unlocking
- Users start at Level 1
- Levels unlock progressively as lessons are completed
- Each level has XP requirements (stored in Level model)
- Completing a lesson unlocks the next level if XP threshold is met

#### XP & Rewards
- **Exercise Completion**: 5-10 XP per exercise (varies by exercise)
- **Streak Multiplier**: 1.0 + (streak * 0.1), max 2.0x
- **Lesson Completion**: Lesson XP reward (stored in Lesson model)
- **Milestone Completion**: 50+ XP (varies by milestone)
- **Quest Completion**: Quest-specific XP rewards

#### Currency System
- **Coins**: Earned at 1 coin per 2 XP
- **Gems**: Earned through quest completion
- Used for rewards and future features

### 2. **Exercise Scoring Logic**

#### Scoring Threshold
- **Pass Threshold**: 70% (0.7)
- Below threshold: Exercise marked incorrect, user can retry
- Above threshold: Exercise marked correct, XP awarded

#### Exercise Type-Specific Scoring

**Select/Scenario Exercises**:
- Exact match with correct answers: 1.0
- Partial match (some correct): 0.5
- No match: 0.0

**Match/Order Exercises**:
- Exact order match: 1.0
- Partial match: Similarity ratio (matches / total)

**Rewrite Exercises**:
- Exact text match: 1.0
- Word overlap: Jaccard similarity (intersection / union)

**Listen/Speak Exercises**:
- Placeholder: 0.8 (production would use speech-to-text comparison)

**Milestone Exercises**:
- Weighted rubric scoring
- Default criteria: clarity, structure, presence, influence
- Overall score: Weighted sum of rubric scores
- Pass threshold: 70%

### 3. **Streak System**

#### Streak Calculation
- **First Activity**: Streak = 1
- **Same Day**: Streak unchanged
- **Exactly 1 Day Gap**: Streak increments
- **2+ Days Gap**: Streak resets to 1

#### Streak Multiplier
- Applied to exercise XP rewards
- Formula: `min(1.0 + (streak * 0.1), 2.0)`
- Maximum multiplier: 2.0x

### 4. **Quest System**

#### Quest Types
- **Daily**: Resets daily, short-term goals
- **Weekly**: Resets weekly, medium-term goals
- **Special**: Limited-time events

#### Quest Requirements
- XP-based: Earn X XP
- Lesson-based: Complete X lessons
- Streak-based: Maintain X-day streak

#### Quest Progress Tracking
- Stored in UserQuest.progress JSON field
- Tracks specific requirements dynamically
- Updates on relevant user actions

### 5. **Leaderboard System**

#### Ranking Criteria
- Primary: Total XP (descending)
- Secondary: Current streak (descending)
- Updated on user activity

#### League System
- **Bronze**: Entry level
- **Silver**: Mid-tier
- **Gold**: High-tier
- **Diamond**: Top-tier

#### Unlocking
- Leaderboard unlocks after N lessons (implementation detail)

### 6. **Milestone Challenges**

#### Purpose
- Speech recording assessments at level completion
- Tests practical application of learned skills

#### Scoring
- Rubric-based with multiple criteria
- Weighted scoring system
- AI feedback (placeholder - production uses AI)

#### Rewards
- XP: 50+ (varies by milestone)
- Coins: 20+ (varies by milestone)
- Level unlock: Unlocks next level if passed

### 7. **AI Chat Integration**

#### Webhook Architecture
- Client → Django → n8n Webhook → AI Service → Response
- Configurable via `AI_CHAT_WEBHOOK_URL` environment variable
- Default: `https://speak-pro-app.fly.dev/webhook/9527da75-7725-439b-9bce-920dcac70acb`

#### User Context
- Includes in request:
  - Current level
  - Total XP
  - Current streak
  - Username

#### Response Handling
- Supports multiple response formats:
  - JSON with `response`, `message`, `text`, `answer`, `content`, `output`
  - OpenAI-style format with `choices`
  - Plain text
  - Lists

#### Error Handling
- Timeout: 30 seconds
- HTTP errors: Proper error messages
- Connection errors: User-friendly messages

---

## Frontend Architecture

### Template Structure

#### Base Template (`base.html`)
- **Meta Tags**: SEO, Open Graph, Twitter Cards
- **CSS**: TailwindCSS via CDN
- **JavaScript**: HTMX, Alpine.js
- **PWA**: Progressive Web App meta tags
- **Navigation**: Responsive header with user menu

#### Landing Page (`landing/index.html`)
- **Sections**:
  - Hero section
  - How it works
  - Pricing
  - Testimonials
  - FAQ
  - Footer
- **Purpose**: Marketing/onboarding for non-authenticated users

#### Home Page (`home.html`)
- **For Authenticated Users**:
  - Dashboard with current level
  - Active quests
  - Leaderboard position
  - Level progression cards
- **Purpose**: Main dashboard

#### Lesson Runner (`lesson_runner.html`)
- **Structure**:
  - Sidebar with lesson info
  - Exercise cards (one per exercise)
  - Progress tracking
  - Exercise type-specific UI components
- **Interactivity**:
  - HTMX for dynamic updates
  - JavaScript for exercise submission
  - Audio recording for speak/milestone exercises
- **Exercise Types**:
  - Select: Radio/checkbox inputs
  - Match: Drag-and-drop interface
  - Rewrite: Textarea input
  - Listen: Audio playback + selection
  - Speak: Audio recording button
  - Scenario: Multiple choice
  - FourPics: Image selection + text input

#### AI Chat (`ai_chat.html`)
- **Interface**: Chat-like UI
- **Features**:
  - Message input
  - Send button
  - Chat history display
  - Loading states

### Styling Approach
- **TailwindCSS**: Utility-first CSS framework
- **Design System**:
  - Gradient backgrounds (purple to cyan)
  - Dark theme with glassmorphism effects
  - Responsive design (mobile-first)
  - Custom animations and transitions

### JavaScript Architecture
- **HTMX**: For server-side interactions without full page reloads
- **Alpine.js**: For reactive UI components
- **Vanilla JavaScript**: For exercise-specific logic (audio recording, drag-and-drop)

---

## Data Flow & User Journeys

### User Registration Flow

```
1. User visits landing page (/)
2. Clicks "Sign Up"
3. Fills signup form (username, email, password, name)
4. POST /signup/
5. View creates User and Profile
6. Sets default preferences (daily_goal_minutes=5, current_level=1)
7. Logs user in
8. Sets session flag 'signup_completed'
9. Redirects to home (/)
10. Home page shows dashboard with Level 1 unlocked
```

### Lesson Completion Flow

```
1. User clicks "Start Lesson" on home page
2. GET /lesson/<id>/
3. Lesson runner loads lesson and exercises
4. User completes exercises one by one
5. For each exercise:
   a. User interacts with exercise UI
   b. Clicks "Check" button
   c. POST /exercise/<id>/submit/
   d. View calculates score
   e. Creates ExerciseAttempt
   f. Updates Profile (XP, coins)
   g. Updates streak
   h. Returns JSON with feedback
6. After all exercises complete:
   a. POST /lesson/<id>/complete/
   b. View awards lesson XP
   c. Unlocks next level if applicable
   d. Returns JSON with next level info
7. User sees completion message
8. Redirects to next lesson or home
```

### Milestone Challenge Flow

```
1. User completes all lessons in a level
2. Clicks "Take Milestone Challenge"
3. GET /milestone/<level_id>/
4. Milestone challenge page loads
5. User records speech (audio)
6. POST /milestone/<id>/submit/
7. View processes audio:
   a. Calculates rubric scores (placeholder)
   b. Calculates overall score
   c. Checks pass threshold (70%)
8. Creates MilestoneAttempt
9. If passed:
   a. Awards XP and coins
   b. Unlocks next level
   c. Creates rewards
10. Returns JSON with results
11. User sees pass/fail feedback
```

### Quest Flow

```
1. User visits quests page
2. GET /quests/
3. View loads active quests and user progress
4. User clicks "Start Quest"
5. POST /quests/<id>/start/
6. View creates UserQuest with initial progress
7. User completes quest requirements (XP, lessons, streak)
8. Quest progress updates automatically (via signal or manual check)
9. User clicks "Complete Quest"
10. POST /quests/<id>/complete/
11. View:
    a. Validates requirements met
    b. Marks quest as completed
    c. Awards rewards (XP, coins, gems)
    d. Updates Profile
12. User sees completion message
```

### AI Chat Flow

```
1. User clicks "AI Coach" button
2. GET /ai-chat/
3. AI chat interface loads
4. User types message
5. Clicks "Send"
6. POST /ai-chat/send/
7. View:
   a. Prepares payload with user context
   b. POST to n8n webhook
   c. Waits for response (30s timeout)
   d. Parses response (handles multiple formats)
8. Returns JSON with AI response
9. Frontend displays response in chat
10. User can continue conversation
```

### Streak Update Flow

```
1. User completes an exercise
2. Exercise submission triggers update_user_streak()
3. Function:
   a. Gets or creates Streak record
   b. Calculates time since last activity
   c. Updates streak:
      - If >24 hours: Reset to 1
      - If exactly 1 day: Increment
      - If same day: No change
   d. Updates longest streak if needed
   e. Updates last_activity timestamp
   f. Syncs with Profile model
4. Streak multiplier applied to next exercise XP
```

---

## External Integrations

### 1. **n8n Webhook (AI Chat)**

**Purpose**: AI-powered chat assistant for on-demand help

**Configuration**:
- Environment variable: `AI_CHAT_WEBHOOK_URL`
- Default: `https://speak-pro-app.fly.dev/webhook/9527da75-7725-439b-9bce-920dcac70acb`

**Request Format**:
```json
{
  "message": "User's message text",
  "user_context": {
    "level": 1,
    "total_xp": 100,
    "current_streak": 5,
    "username": "user123"
  }
}
```

**Response Handling**:
- Supports multiple response formats
- Handles JSON, plain text, and structured responses
- 30-second timeout
- Comprehensive error handling

### 2. **Stripe (Payments)**

**Status**: Configured but not fully implemented

**Configuration**:
- `STRIPE_PUBLISHABLE_KEY`: Public key
- `STRIPE_SECRET_KEY`: Secret key
- `STRIPE_WEBHOOK_SECRET`: Webhook secret

**Models**:
- `SubscriptionPlan`: Plan definitions with Stripe price IDs
- `Subscription`: User subscriptions with Stripe IDs

**Future Implementation**:
- Payment processing
- Subscription management
- Webhook handlers for subscription events

### 3. **AWS S3 (Media Storage)**

**Status**: Configured but not fully implemented

**Configuration**:
- `AWS_ACCESS_KEY_ID`: Access key
- `AWS_SECRET_ACCESS_KEY`: Secret key
- `AWS_STORAGE_BUCKET_NAME`: Bucket name
- `AWS_S3_REGION_NAME`: Region

**Future Implementation**:
- Audio recording storage
- Image uploads
- Media file serving

---

## Deployment & Configuration

### Environment Setup

#### Required Environment Variables
- `AI_CHAT_WEBHOOK_URL`: n8n webhook URL (optional, has default)
- `OPENAI_API_KEY`: OpenAI API key (for future AI features)
- `SECRET_KEY`: Django secret key (production)
- `DEBUG`: Debug mode (False in production)
- `ALLOWED_HOSTS`: Allowed hostnames

#### Database
- **Development**: SQLite3 (`db.sqlite3`)
- **Production**: Can be switched to PostgreSQL/MySQL

### Deployment Configuration

#### Railway Deployment
- **Platform**: Railway
- **URL**: `tuliamvppwa-production.up.railway.app`
- **Server**: Gunicorn
- **Static Files**: WhiteNoise
- **Database**: SQLite3 (can be upgraded)

#### Static Files
- **Static Root**: `staticfiles/`
- **Media Root**: `media/`
- **Serving**: WhiteNoise in production

### Security Settings

#### CSRF Protection
- `CSRF_TRUSTED_ORIGINS`: Production domain
- Django's built-in CSRF middleware

#### CORS
- Configured for localhost development
- Can be expanded for production domains

#### Authentication
- Django's built-in authentication
- Session-based authentication
- Login required decorator on protected views

### Logging

**Configuration** (`settings.py`):
- Log file: `logs/django.log`
- Level: INFO
- Handlers: File handler

**Usage**:
- Logging in views for errors
- Error tracking for webhook requests
- User action logging (future enhancement)

---

## Key Design Decisions

### 1. **Progressive Unlocking**
- Levels unlock as users progress
- No strict XP gating (lessons unlock next level directly)
- Encourages continuous learning

### 2. **Streak Multiplier**
- Rewards daily engagement
- Maximum 2x multiplier prevents excessive XP
- Creates habit-forming behavior

### 3. **Flexible Exercise System**
- JSON-based options and answers
- Easy to add new exercise types
- Supports various media types

### 4. **Gamification Balance**
- XP, coins, gems for different purposes
- Streaks for daily engagement
- Quests for structured challenges
- Leaderboards for competition

### 5. **AI Integration**
- Webhook-based for flexibility
- Context-aware responses
- Fallback error handling
- Multiple response format support

### 6. **PWA Architecture**
- Progressive Web App capabilities
- Offline support (future)
- Mobile-friendly design
- Fast loading with CDN resources

---

## Future Enhancements

### Planned Features
1. **Speech Recognition**: Real speech-to-text for listen/speak exercises
2. **AI Scoring**: AI-powered rubric scoring for milestones
3. **Social Features**: Friends, sharing, competitions
4. **Advanced Analytics**: Learning analytics dashboard
5. **Content Management**: Admin interface for content creation
6. **Localization**: Multi-language support
7. **Offline Mode**: PWA offline capabilities
8. **Push Notifications**: Reminder notifications
9. **Video Content**: Video lessons and explanations
10. **Community Features**: Forums, discussions

### Technical Improvements
1. **Database Migration**: PostgreSQL for production
2. **Caching**: Redis for performance
3. **Background Tasks**: Celery for async processing
4. **API Versioning**: REST API for mobile apps
5. **WebSocket Support**: Real-time updates
6. **Testing**: Comprehensive test suite
7. **CI/CD**: Automated deployment pipeline
8. **Monitoring**: Error tracking and analytics

---

## Conclusion

Tulia is a comprehensive learning platform built on Django with a focus on gamification, structured learning, and AI-powered assistance. The architecture is designed to be scalable, flexible, and user-friendly, with clear separation of concerns and a well-structured data model.

The application follows Django best practices and is designed to evolve with additional features and improvements. The current MVP provides a solid foundation for a production-ready learning platform.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Maintained By**: Development Team

