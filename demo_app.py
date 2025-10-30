#!/usr/bin/env python3
"""
Speakopoly Educational App Demo
This script demonstrates the app structure and key features
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.models import (
    Level, Unit, Lesson, Exercise, MilestoneChallenge, District, 
    Reward, Quest, SubscriptionPlan, Profile
)

def demo_app_structure():
    """Demonstrate the app structure and features"""
    
    print("🎯 Speakopoly - Educational Communication App")
    print("=" * 50)
    
    # Show levels
    print("\n📚 Educational Levels:")
    levels = Level.objects.all()
    for level in levels:
        print(f"  Level {level.number}: {level.name}")
        print(f"    Duration: {level.duration_minutes} min")
        print(f"    District: {level.district_name}")
        print(f"    XP Required: {level.xp_required}")
        print()
    
    # Show units and lessons
    print("📖 Units and Lessons:")
    for level in levels:
        units = level.units.all()
        for unit in units:
            print(f"  {unit.name} ({unit.duration_minutes} min)")
            lessons = unit.lessons.all()
            for lesson in lessons:
                exercises = lesson.exercises.count()
                print(f"    - {lesson.name} ({lesson.duration_minutes} min, {exercises} exercises)")
    
    # Show exercise types
    print("\n🎯 Exercise Types Available:")
    exercise_types = Exercise.EXERCISE_TYPES
    for type_code, type_name in exercise_types:
        count = Exercise.objects.filter(exercise_type=type_code).count()
        print(f"  {type_name}: {count} exercises")
    
    # Show districts
    print("\n🏛️ Speakopoly Districts:")
    districts = District.objects.all()
    for district in districts:
        print(f"  {district.name} (Level {district.level.number})")
        print(f"    Coach: {district.coach_name}")
        print(f"    XP Required: {district.xp_required}")
        print()
    
    # Show rewards
    print("🏆 Rewards System:")
    rewards = Reward.objects.all()
    for reward in rewards:
        print(f"  {reward.name} ({reward.get_reward_type_display()})")
        print(f"    Level Required: {reward.level_required}")
        print(f"    XP Required: {reward.xp_required}")
        print()
    
    # Show quests
    print("⚔️ Active Quests:")
    quests = Quest.objects.filter(is_active=True)
    for quest in quests:
        print(f"  {quest.name} ({quest.get_quest_type_display()})")
        print(f"    XP Reward: {quest.xp_reward}")
        print(f"    Coins Reward: {quest.coins_reward}")
        print()
    
    # Show subscription plans
    print("💳 Subscription Plans:")
    plans = SubscriptionPlan.objects.all()
    for plan in plans:
        print(f"  {plan.name}")
        print(f"    Monthly: ${plan.price_monthly}")
        print(f"    Yearly: ${plan.price_yearly}")
        print(f"    Max Family Members: {plan.max_family_members}")
        print()
    
    # Show milestone challenges
    print("🎤 Milestone Challenges:")
    milestones = MilestoneChallenge.objects.all()
    for milestone in milestones:
        print(f"  {milestone.name} (Level {milestone.level.number})")
        print(f"    Duration: {milestone.duration_seconds} seconds")
        print(f"    XP Reward: {milestone.xp_reward}")
        print(f"    Coins Reward: {milestone.coins_reward}")
        print()

def demo_user_journey():
    """Demonstrate a typical user journey"""
    
    print("\n👤 User Journey Example:")
    print("=" * 30)
    
    # Create a demo user profile
    from django.contrib.auth.models import User
    
    # Check if demo user exists
    demo_user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@speakopoly.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    # Set password for demo user
    if created:
        demo_user.set_password('demo123')
        demo_user.save()
    
    if created:
        print("✅ Created demo user")
    else:
        print("✅ Using existing demo user")
    
    # Create or get profile
    profile, created = Profile.objects.get_or_create(
        user=demo_user,
        defaults={
            'current_level': 1,
            'total_xp': 0,
            'current_streak': 0,
            'coins': 0,
            'gems': 0,
            'daily_goal_minutes': 5,
            'learning_goal': 'converse_confidently'
        }
    )
    
    print(f"📊 User Profile:")
    print(f"  Level: {profile.current_level}")
    print(f"  Total XP: {profile.total_xp}")
    print(f"  Current Streak: {profile.current_streak}")
    print(f"  Coins: {profile.coins}")
    print(f"  Daily Goal: {profile.daily_goal_minutes} minutes")
    print(f"  Learning Goal: {profile.learning_goal}")
    
    # Show available content
    print(f"\n📚 Available Content for Level {profile.current_level}:")
    current_level = Level.objects.get(number=profile.current_level)
    units = current_level.units.all()
    
    for unit in units:
        print(f"  {unit.name}")
        lessons = unit.lessons.all()
        for lesson in lessons:
            exercises = lesson.exercises.all()
            print(f"    - {lesson.name} ({len(exercises)} exercises)")
    
    # Show districts available
    print(f"\n🏛️ Available Districts:")
    available_districts = District.objects.filter(
        level__number__lte=profile.current_level,
        xp_required__lte=profile.total_xp
    )
    
    for district in available_districts:
        print(f"  {district.name} (Level {district.level.number})")
        print(f"    Coach: {district.coach_name}")
        print(f"    Description: {district.description}")

def show_technical_features():
    """Show technical implementation features"""
    
    print("\n🔧 Technical Features:")
    print("=" * 30)
    
    features = [
        "✅ Django Models: 15+ models for complete educational system",
        "✅ Authentication: Social login (Google, Apple, Facebook)",
        "✅ REST API: Django REST Framework for mobile/web",
        "✅ Background Tasks: Celery for async processing",
        "✅ Caching: Redis for performance optimization",
        "✅ Media Storage: AWS S3 integration ready",
        "✅ Payments: Stripe integration for subscriptions",
        "✅ Frontend: HTMX + Alpine.js + TailwindCSS",
        "✅ Audio Recording: Browser MediaRecorder API",
        "✅ Gamification: Streaks, quests, rewards, leaderboards",
        "✅ Content Management: Rich content blocks and tips",
        "✅ Scoring System: Exercise-specific algorithms",
        "✅ Progress Tracking: XP, levels, achievements",
        "✅ Subscription Tiers: Free, Super, Super Family",
        "✅ Responsive Design: Mobile-first approach"
    ]
    
    for feature in features:
        print(f"  {feature}")

if __name__ == "__main__":
    try:
        demo_app_structure()
        demo_user_journey()
        show_technical_features()
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo run the full Django app:")
        print("1. Install Python 3.8+ and dependencies")
        print("2. Run: python manage.py makemigrations")
        print("3. Run: python manage.py migrate")
        print("4. Run: python manage.py seed_content")
        print("5. Run: python manage.py runserver")
        print("6. Visit: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("Make sure Django is properly set up and the database is migrated.")
