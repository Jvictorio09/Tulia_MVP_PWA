# Tulia – UX Process and Storyboard

## Purpose
This document summarizes the end-to-end user experience for Tulia (Speakopoly), from onboarding to mastery, and provides practical setup instructions for running a local demo with seeded content.

---

## Setup and Seeding

### Prerequisites
- Python 3.8+
- Virtual environment recommended

### Install and run
1. Create/activate your venv
2. Install dependencies
3. Apply migrations
4. (Optional) Create superuser
5. Seed demo lesson content
6. Run the server

```bash
# from myProject/
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
# optional
python manage.py createsuperuser
# seed demo content
python insert_lesson.py
# run
python manage.py runserver
```

### What the seed adds
- Level 1: “Foundations”
- Unit 1: “Awareness & Foundations”
- Lesson 1: “Clarity vs. Jargon”
- 6 Exercises: select, match, rewrite, listen, speak, scenario
- Tip sheet + content blocks
- District: “City Square”
- Milestone: “30-Second Introduction”

---

## Core UX Pillars
- Clarity-first communication practice
- Short, focused lessons (5–10 minutes)
- Gamified progress: XP, coins, streaks, rewards, levels
- Milestone recordings with rubric-based feedback
- Optional AI help (RAG) for hints and explanations

---

## User Journey (Happy Path)

### 1) Onboarding
- User lands on Home
- Signs up with email/password
- Auto-generated Profile with default goals

### 2) Explore the City (Home)
- Sees current Level and accessible Districts
- Active Quests surfaced for quick wins
- Leaderboard card shown after initial progress

### 3) Start Learning
- Navigates to Levels → selects Level 1
- Opens Lesson Runner for “Clarity vs. Jargon”
- Lesson header shows objective, time, and tip entry point

### 4) Lesson Runner Flow
- Exercise 1 (Select): Choose clearer sentence → instant feedback
- Exercise 2 (Match): Map jargon to plain English → partial credit allowed
- Exercise 3 (Rewrite): Rewrite with clarity → text-similarity scoring
- Exercise 4 (Listen): Tap the words you hear → recognition practice
- Exercise 5 (Speak): Record a simple sentence → placeholder scoring now
- Exercise 6 (Scenario): Choose best approach for a situation
- Each correct step grants XP; streak multiplier may apply
- Tip Sheet and Content Blocks available as in-lesson guidance

### 5) Milestone Challenge
- Unlocks per level (e.g., 30-second intro)
- Records audio; receives rubric-style scores (clarity, structure, presence, influence)
- Passing grants larger XP/coins and unlocks next Level

### 6) Progress & Rewards
- Profile shows total XP, recent attempts, rewards
- Streak page encourages daily practice
- Leaderboard shows relative standing after enough activity
- Quests offer daily/weekly goals with rewards on completion

### 7) Growth & Conversion (Optional)
- Subscription plans appear contextually (e.g., after milestone)
- Family plan upsell path available

---

## Screen-by-Screen Storyboard

1. Home (City Map)
   - Panels: Current Level, Districts, Active Quests, Leaderboard teaser
   - CTA: Continue Lesson / Start Milestone / View Quests

2. Levels
   - Grid/list of Levels with lock states and XP requirements
   - Selecting Level drills into Units and Lessons

3. Lesson Runner
   - Header: Title, time estimate, objective, tip sheet link
   - Body: Active Exercise panel (HTMX interactions)
   - Footer: Progress indicator, Next action

4. Exercise Detail (Modal/Inline)
   - Prompt, stimuli (text/audio), input controls
   - Feedback: correct/incorrect, explanation, XP earned

5. Tip Sheet
   - Concise rules and rewrite examples
   - Quick-close to return to exercise

6. Milestone Challenge
   - Record UI + countdown timer
   - Submit → rubric feedback → pass/fail outcome + rewards

7. Profile
   - XP, streak, recent attempts, earned rewards

8. Quests
   - Daily/Weekly/Special quests; start/complete flows; rewards

9. Leaderboard
   - Top entries + user’s position; league badges

---

## Data and Scoring Model (Simplified)
- Exercises: type-specific scoring (exact match, order similarity, rewrite similarity, placeholders for audio)
- Streak: daily activity updates current/longest streak
- XP/Coins: per exercise; milestone larger rewards
- Level Unlock: milestone pass increments level and triggers rewards

---

## Integrations (Planned)
- n8n RAG Help: contextual lesson help and Q&A
- Stripe: subscriptions (monthly/yearly, family)
- S3: media storage for recordings
- OpenAI: advanced speech analysis and coaching

---

## Testing the Flow
- Create an account, visit Levels, open the seeded lesson
- Complete exercises → watch XP and streak update
- Try the Milestone Challenge
- Check Profile, Streak, Quests, Leaderboard pages

---

## Troubleshooting
- No content? Ensure migrations ran and rerun `python insert_lesson.py`
- Auth redirects? Log in at `/login/` first
- Static/media in DEBUG mode served by Django per settings

---

## Next Steps
- Add more Units/Lessons per Level
- Enhance audio exercises with real STT scoring
- Integrate n8n RAG help on Lesson Runner screens
- Add progressive disclosures and micro-coaching moments
