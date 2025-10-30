#!/usr/bin/env python3
"""
Seed script for Tulia quests.

Run: python insert_quests.py

This script creates daily, weekly, and special quests with various requirements and rewards.
"""

import os
import sys
from pathlib import Path


def setup_django():
    project_dir = Path(__file__).parent
    sys.path.insert(0, str(project_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
    import django
    django.setup()


def main():
    setup_django()
    from django.db import transaction
    from myApp.models import Quest
    from django.utils import timezone
    from datetime import timedelta

    # Wipe existing quests
    print('🗑️  Clearing existing quests...')
    with transaction.atomic():
        Quest.objects.all().delete()

    print('🌱 Seeding quests...')

    with transaction.atomic():
        # DAILY QUESTS
        daily_quests = [
            {
                'name': 'Morning Warm-up',
                'description': 'Complete 3 exercises to start your day strong!',
                'quest_type': 'daily',
                'lessons_required': 1,
                'xp_reward': 25,
                'coins_reward': 10,
                'gems_reward': 0,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=1),
            },
            {
                'name': 'Daily Streak',
                'description': 'Maintain your streak by completing at least one lesson today.',
                'quest_type': 'daily',
                'lessons_required': 1,
                'xp_reward': 30,
                'coins_reward': 15,
                'gems_reward': 1,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=1),
            },
            {
                'name': 'Rapid Learner',
                'description': 'Complete 5 exercises in a single session.',
                'quest_type': 'daily',
                'lessons_required': 1,
                'xp_reward': 40,
                'coins_reward': 20,
                'gems_reward': 0,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=1),
            },
        ]

        # WEEKLY QUESTS
        weekly_quests = [
            {
                'name': 'Week Warrior',
                'description': 'Complete 7 lessons this week and earn big rewards!',
                'quest_type': 'weekly',
                'lessons_required': 7,
                'xp_reward': 200,
                'coins_reward': 100,
                'gems_reward': 5,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=7),
            },
            {
                'name': 'Streak Master',
                'description': 'Maintain a 7-day streak to unlock bonus rewards!',
                'quest_type': 'weekly',
                'streak_required': 7,
                'xp_reward': 250,
                'coins_reward': 125,
                'gems_reward': 7,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=7),
            },
            {
                'name': 'XP Collector',
                'description': 'Earn 500 XP this week to become an XP champion!',
                'quest_type': 'weekly',
                'xp_required': 500,
                'xp_reward': 300,
                'coins_reward': 150,
                'gems_reward': 10,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=7),
            },
        ]

        # SPECIAL QUESTS
        special_quests = [
            {
                'name': 'Level Up Champion',
                'description': 'Reach Level 3 and unlock exclusive rewards!',
                'quest_type': 'special',
                'xp_required': 0,
                'xp_reward': 500,
                'coins_reward': 250,
                'gems_reward': 25,
                'is_active': True,
                'expires_at': None,  # Never expires
            },
            {
                'name': 'Perfect Score',
                'description': 'Get 5 perfect scores (100%) in exercises to master precision!',
                'quest_type': 'special',
                'lessons_required': 5,
                'xp_reward': 150,
                'coins_reward': 75,
                'gems_reward': 5,
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=30),
            },
            {
                'name': 'Milestone Maven',
                'description': 'Complete a milestone challenge to prove your speaking skills!',
                'quest_type': 'special',
                'lessons_required': 1,
                'xp_reward': 400,
                'coins_reward': 200,
                'gems_reward': 20,
                'is_active': True,
                'expires_at': None,  # Never expires
            },
        ]

        # Create all quests
        all_quests = daily_quests + weekly_quests + special_quests
        created_count = 0
        
        for quest_data in all_quests:
            quest, created = Quest.objects.get_or_create(
                name=quest_data['name'],
                defaults=quest_data
            )
            if created:
                created_count += 1

    print(f'\n✅ Created {created_count} quests successfully!')
    print(f'  - {len(daily_quests)} Daily quests')
    print(f'  - {len(weekly_quests)} Weekly quests')
    print(f'  - {len(special_quests)} Special quests')
    print('\nNext: Run your server and check the quests page!')


if __name__ == '__main__':
    main()
