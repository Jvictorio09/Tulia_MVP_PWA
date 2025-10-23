from django.core.management.base import BaseCommand
from myApp.models import (
    Level, Unit, Lesson, Exercise, MilestoneChallenge, District, 
    Reward, Quest, SubscriptionPlan
)


class Command(BaseCommand):
    help = 'Seed the database with Level 1 educational content'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with educational content...')
        
        # Create Level 1: Awareness & Foundations
        level1, created = Level.objects.get_or_create(
            number=1,
            defaults={
                'name': 'Awareness & Foundations',
                'description': 'Master the fundamentals of high-stakes communication. Learn about audience psychology, clarity vs jargon, and building presence.',
                'duration_minutes': 75,
                'xp_required': 0,
                'milestone_duration_seconds': 30,
                'district_name': 'Foundations District',
                'district_description': 'The starting point of your communication journey. Master the basics here.',
                'coins_reward': 100,
                'gems_reward': 20,
            }
        )
        
        if created:
            self.stdout.write(f'Created Level 1: {level1.name}')
        
        # Create Districts for Level 1
        districts_data = [
            {
                'name': 'Amphitheater',
                'description': 'Practice your public speaking in this grand venue',
                'coach_name': 'Marcus Aurelius',
                'coach_description': 'Master of presence and authority',
                'xp_required': 0,
            },
            {
                'name': 'Forum',
                'description': 'Engage in structured debates and discussions',
                'coach_name': 'Cicero',
                'coach_description': 'Expert in persuasive communication',
                'xp_required': 25,
            },
            {
                'name': 'Market',
                'description': 'Learn to communicate in high-pressure business settings',
                'coach_name': 'Athena',
                'coach_description': 'Goddess of wisdom and strategic communication',
                'xp_required': 50,
            }
        ]
        
        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                level=level1,
                name=district_data['name'],
                defaults=district_data
            )
            if created:
                self.stdout.write(f'Created District: {district.name}')
        
        # Create Units for Level 1
        units_data = [
            {
                'name': 'High-Stakes Context',
                'description': 'Understand when communication really matters',
                'order': 1,
                'duration_minutes': 15,
            },
            {
                'name': 'Audience Psychology',
                'description': 'Learn to read and connect with your audience',
                'order': 2,
                'duration_minutes': 20,
            },
            {
                'name': 'Clarity vs Jargon',
                'description': 'Master the art of clear, accessible communication',
                'order': 3,
                'duration_minutes': 20,
            },
            {
                'name': 'Building Presence',
                'description': 'Develop confidence and authority in your delivery',
                'order': 4,
                'duration_minutes': 20,
            }
        ]
        
        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                level=level1,
                order=unit_data['order'],
                defaults=unit_data
            )
            if created:
                self.stdout.write(f'Created Unit: {unit.name}')
        
        # Create Lessons for Unit 1: High-Stakes Context
        unit1 = Unit.objects.get(level=level1, order=1)
        lessons_data = [
            {
                'name': 'What Makes Communication High-Stakes?',
                'description': 'Identify situations where communication has significant consequences',
                'order': 1,
                'duration_minutes': 5,
                'xp_reward': 10,
                'tip_sheet': 'High-stakes communication occurs when the outcome significantly impacts your goals, relationships, or reputation. Examples include job interviews, client presentations, difficult conversations, and public speaking.',
                'learning_objectives': 'Identify high-stakes situations, understand the consequences of poor communication, recognize the importance of preparation.',
            },
            {
                'name': 'Stakes Assessment Framework',
                'description': 'Learn to evaluate the stakes in any communication situation',
                'order': 2,
                'duration_minutes': 5,
                'xp_reward': 10,
                'tip_sheet': 'Use the RICE framework: Risk (what could go wrong), Impact (consequences), Control (your influence), and Expectations (what others expect).',
                'learning_objectives': 'Apply stakes assessment, prioritize communication efforts, make informed decisions about preparation.',
            },
            {
                'name': 'Practice: Stakes Identification',
                'description': 'Practice identifying stakes in various scenarios',
                'order': 3,
                'duration_minutes': 5,
                'xp_reward': 15,
                'tip_sheet': 'Look for indicators like: formal settings, important audiences, significant outcomes, time pressure, and personal/professional consequences.',
                'learning_objectives': 'Practice stakes identification, develop situational awareness, build confidence in assessment skills.',
            }
        ]
        
        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                unit=unit1,
                order=lesson_data['order'],
                defaults=lesson_data
            )
            if created:
                self.stdout.write(f'Created Lesson: {lesson.name}')
                
                # Create exercises for each lesson
                self.create_exercises_for_lesson(lesson)
        
        # Create Milestone Challenge for Level 1
        milestone, created = MilestoneChallenge.objects.get_or_create(
            level=level1,
            defaults={
                'name': '30-Second Introduction',
                'description': 'Record a compelling 30-second introduction that demonstrates your communication skills',
                'duration_seconds': 30,
                'rubric': {
                    'weights': {
                        'clarity': 0.3,
                        'structure': 0.3,
                        'presence': 0.2,
                        'influence': 0.2,
                    },
                    'criteria': {
                        'clarity': 'Clear pronunciation, appropriate pace, easy to understand',
                        'structure': 'Logical flow, clear opening and closing',
                        'presence': 'Confident delivery, engaging tone',
                        'influence': 'Compelling content, memorable message',
                    }
                },
                'xp_reward': 50,
                'coins_reward': 25,
            }
        )
        
        if created:
            self.stdout.write(f'Created Milestone: {milestone.name}')
        
        # Create Rewards
        rewards_data = [
            {
                'name': 'Clarity Coin',
                'reward_type': 'coin',
                'description': 'Earned for mastering clear communication',
                'level_required': 1,
                'xp_required': 25,
            },
            {
                'name': 'Level 1 Mastery Badge',
                'reward_type': 'badge',
                'description': 'Completed Level 1: Awareness & Foundations',
                'level_required': 1,
                'xp_required': 100,
            },
            {
                'name': 'First Steps Token',
                'reward_type': 'token',
                'description': 'Your first communication milestone',
                'level_required': 1,
                'xp_required': 10,
            }
        ]
        
        for reward_data in rewards_data:
            reward, created = Reward.objects.get_or_create(
                name=reward_data['name'],
                defaults=reward_data
            )
            if created:
                self.stdout.write(f'Created Reward: {reward.name}')
        
        # Create Quests
        quests_data = [
            {
                'name': 'Daily Practice',
                'description': 'Complete any lesson to maintain your streak',
                'quest_type': 'daily',
                'xp_required': 10,
                'xp_reward': 5,
                'coins_reward': 10,
            },
            {
                'name': 'Weekend Warrior',
                'description': 'Complete 3 lessons in a single day',
                'quest_type': 'weekly',
                'lessons_required': 3,
                'xp_reward': 25,
                'coins_reward': 50,
            },
            {
                'name': 'Streak Master',
                'description': 'Maintain a 7-day streak',
                'quest_type': 'special',
                'streak_required': 7,
                'xp_reward': 100,
                'coins_reward': 100,
            }
        ]
        
        for quest_data in quests_data:
            quest, created = Quest.objects.get_or_create(
                name=quest_data['name'],
                defaults=quest_data
            )
            if created:
                self.stdout.write(f'Created Quest: {quest.name}')
        
        # Create Subscription Plans
        plans_data = [
            {
                'name': 'Free',
                'description': 'Basic access to Level 1 content',
                'price_monthly': 0,
                'price_yearly': 0,
                'features': ['Level 1 access', 'Basic exercises', 'Community features'],
                'max_family_members': 1,
            },
            {
                'name': 'Super',
                'description': 'Unlock all levels and premium features',
                'price_monthly': 9.99,
                'price_yearly': 99.99,
                'features': ['All levels', 'Advanced AI feedback', 'No ads', 'Premium exercises', 'Progress tracking'],
                'max_family_members': 1,
            },
            {
                'name': 'Super Family',
                'description': 'Super features for the whole family',
                'price_monthly': 19.99,
                'price_yearly': 199.99,
                'features': ['All Super features', 'Up to 6 family members', 'Family progress tracking', 'Parental controls'],
                'max_family_members': 6,
            }
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created Plan: {plan.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with Level 1 content!')
        )

    def create_exercises_for_lesson(self, lesson):
        """Create exercises for a lesson based on its content"""
        
        if lesson.name == 'What Makes Communication High-Stakes?':
            # Multiple choice exercise
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=1,
                defaults={
                    'exercise_type': 'select',
                    'prompt': 'Which of the following situations would be considered high-stakes communication?',
                    'options': [
                        'Asking a colleague for a coffee break',
                        'Presenting quarterly results to the board',
                        'Chatting with friends at lunch',
                        'Ordering food at a restaurant'
                    ],
                    'correct_answers': [1],  # Presenting to board
                    'xp_reward': 5,
                    'feedback_correct': 'Correct! Board presentations have high stakes due to significant business impact.',
                    'feedback_incorrect': 'Think about situations where the outcome has major consequences for your career or business.',
                }
            )
            
            # Scenario exercise
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=2,
                defaults={
                    'exercise_type': 'select',
                    'prompt': 'You need to tell your team that the project deadline has been moved up by two weeks. This is:',
                    'options': [
                        'Low-stakes communication',
                        'Medium-stakes communication',
                        'High-stakes communication',
                        'Not a communication situation'
                    ],
                    'correct_answers': [2],  # High-stakes
                    'xp_reward': 5,
                    'feedback_correct': 'Exactly! This affects team morale, project success, and your credibility as a leader.',
                    'feedback_incorrect': 'Consider the impact on team morale, project success, and your relationship with the team.',
                }
            )
        
        elif lesson.name == 'Stakes Assessment Framework':
            # Match exercise
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=1,
                defaults={
                    'exercise_type': 'match',
                    'prompt': 'Match each component of the RICE framework with its description:',
                    'options': [
                        'Risk - What could go wrong',
                        'Impact - Consequences of the outcome',
                        'Control - Your influence over the situation',
                        'Expectations - What others expect from you'
                    ],
                    'correct_answers': [0, 1, 2, 3],
                    'xp_reward': 8,
                    'feedback_correct': 'Perfect! The RICE framework helps you systematically assess communication stakes.',
                    'feedback_incorrect': 'Review the RICE framework: Risk, Impact, Control, and Expectations.',
                }
            )
            
            # Rewrite exercise
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=2,
                defaults={
                    'exercise_type': 'rewrite',
                    'prompt': 'Rewrite this message to better communicate the stakes: "We need to talk about the project."',
                    'stimulus_text': 'We need to talk about the project.',
                    'reference_rewrite': 'I need to discuss some critical issues with the project that could impact our deadline and budget.',
                    'xp_reward': 10,
                    'feedback_correct': 'Great! You\'ve made the stakes clear and specific.',
                    'feedback_incorrect': 'Try to be more specific about what\'s at stake and why the conversation is important.',
                }
            )
        
        elif lesson.name == 'Practice: Stakes Identification':
            # Multiple choice with multiple correct answers
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=1,
                defaults={
                    'exercise_type': 'select',
                    'prompt': 'Which indicators suggest high-stakes communication? (Select all that apply)',
                    'options': [
                        'Formal setting or venue',
                        'Important audience members present',
                        'Significant potential outcomes',
                        'Time pressure or deadline',
                        'Casual conversation with friends'
                    ],
                    'correct_answers': [0, 1, 2, 3],  # All except casual conversation
                    'xp_reward': 10,
                    'feedback_correct': 'Excellent! You\'ve identified the key indicators of high-stakes communication.',
                    'feedback_incorrect': 'Look for formal settings, important audiences, significant outcomes, and time pressure.',
                }
            )
            
            # Scenario-based exercise
            Exercise.objects.get_or_create(
                lesson=lesson,
                order=2,
                defaults={
                    'exercise_type': 'select',
                    'prompt': 'You\'re about to give a presentation to potential investors. Rate the stakes:',
                    'options': [
                        'Low - Just another presentation',
                        'Medium - Somewhat important',
                        'High - Critical for funding',
                        'Extreme - Make or break for the company'
                    ],
                    'correct_answers': [3],  # Extreme stakes
                    'xp_reward': 8,
                    'feedback_correct': 'Exactly! Investor presentations often determine the future of your company.',
                    'feedback_incorrect': 'Consider the potential impact on your company\'s funding and future.',
                }
            )
