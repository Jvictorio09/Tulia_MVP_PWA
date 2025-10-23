from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, F, Count, Sum
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
import json
import logging

from .models import (
    Profile, Level, Unit, Lesson, Exercise, ExerciseAttempt,
    MilestoneChallenge, MilestoneAttempt, District, Reward,
    UserReward, Streak, Quest, UserQuest, LeaderboardEntry,
    SubscriptionPlan, Subscription, ContentBlock
)

logger = logging.getLogger(__name__)


def login_view(request):
    """Simple login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'myApp/auth/login.html')


def signup_view(request):
    """Simple signup view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Create profile
            Profile.objects.create(
                user=user,
                daily_goal_minutes=5,
                learning_goal='converse_confidently'
            )
            login(request, user)
            return redirect('home')
    
    return render(request, 'myApp/auth/signup.html')


def logout_view(request):
    """Simple logout view"""
    logout(request)
    return redirect('home')


def home(request):
    """Home page with Speakopoly city map"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        
        # Get user's current level and available districts
        current_level = profile.current_level
        levels = Level.objects.filter(number__lte=current_level + 1).order_by('number')
        districts = District.objects.filter(level__in=levels)
        
        # Get user's active quests
        active_quests = Quest.objects.filter(is_active=True)
        user_quests = UserQuest.objects.filter(user=request.user, quest__in=active_quests)
        
        # Get leaderboard position
        try:
            leaderboard_entry = LeaderboardEntry.objects.get(user=request.user)
        except LeaderboardEntry.DoesNotExist:
            leaderboard_entry = None
        
        context = {
            'profile': profile,
            'levels': levels,
            'districts': districts,
            'user_quests': user_quests,
            'leaderboard_entry': leaderboard_entry,
        }
    else:
        context = {}
    
    return render(request, 'myApp/home.html', context)


@login_required
def lesson_runner(request, lesson_id):
    """Interactive lesson runner with HTMX"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    exercises = lesson.exercises.all().order_by('order')
    
    # Get user's progress for this lesson
    completed_exercises = ExerciseAttempt.objects.filter(
        user=request.user,
        exercise__lesson=lesson,
        is_correct=True
    ).values_list('exercise_id', flat=True)
    
    context = {
        'lesson': lesson,
        'exercises': exercises,
        'completed_exercises': completed_exercises,
    }
    
    return render(request, 'myApp/lesson_runner.html', context)


@login_required
def exercise_detail(request, exercise_id):
    """Individual exercise view with HTMX"""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    # Get user's previous attempts
    attempts = ExerciseAttempt.objects.filter(
        user=request.user,
        exercise=exercise
    ).order_by('-created_at')
    
    context = {
        'exercise': exercise,
        'attempts': attempts,
        'next_attempt': attempts.count() + 1 if attempts.count() < exercise.max_attempts else None,
    }
    
    return render(request, 'myApp/exercise_detail.html', context)


@login_required
@require_http_methods(["POST"])
def submit_exercise(request, exercise_id):
    """Submit exercise attempt via HTMX"""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    user = request.user
    
    try:
        data = json.loads(request.body)
        user_response = data.get('response', [])
        duration_seconds = data.get('duration', 0)
        audio_recording = data.get('audio_recording', '')
        
        # Calculate score based on exercise type
        score = calculate_exercise_score(exercise, user_response)
        is_correct = score >= 0.7  # 70% threshold
        
        # Calculate XP with streak multiplier
        profile = user.profile
        streak_multiplier = min(1.0 + (profile.current_streak * 0.1), 2.0)  # Max 2x multiplier
        xp_earned = int(exercise.xp_reward * streak_multiplier)
        
        # Create attempt
        attempt = ExerciseAttempt.objects.create(
            user=user,
            exercise=exercise,
            attempt_number=ExerciseAttempt.objects.filter(user=user, exercise=exercise).count() + 1,
            user_response=user_response,
            audio_recording=audio_recording,
            duration_seconds=duration_seconds,
            is_correct=is_correct,
            score=score,
            xp_earned=xp_earned
        )
        
        # Update user progress
        if is_correct:
            profile.total_xp += xp_earned
            profile.coins += xp_earned // 2  # 1 coin per 2 XP
            profile.save()
            
            # Update streak
            update_user_streak(user)
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'score': score,
            'xp_earned': xp_earned,
            'feedback': exercise.feedback_correct if is_correct else exercise.feedback_incorrect,
            'next_exercise': get_next_exercise(exercise),
        })
        
    except Exception as e:
        logger.error(f"Error submitting exercise: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


def calculate_exercise_score(exercise, user_response):
    """Calculate score for different exercise types"""
    if exercise.exercise_type == 'select':
        correct_answers = exercise.correct_answers
        if set(user_response) == set(correct_answers):
            return 1.0
        elif any(answer in correct_answers for answer in user_response):
            return 0.5  # Partial credit
        else:
            return 0.0
    
    elif exercise.exercise_type == 'match':
        # For match exercises, compare order
        correct_answers = exercise.correct_answers
        if user_response == correct_answers:
            return 1.0
        else:
            # Calculate similarity
            matches = sum(1 for i, answer in enumerate(user_response) 
                         if i < len(correct_answers) and answer == correct_answers[i])
            return matches / len(correct_answers) if correct_answers else 0.0
    
    elif exercise.exercise_type == 'rewrite':
        # For rewrite exercises, use simple text similarity
        reference = exercise.reference_rewrite.lower().strip()
        user_text = ' '.join(user_response).lower().strip()
        
        if user_text == reference:
            return 1.0
        else:
            # Simple word overlap scoring
            ref_words = set(reference.split())
            user_words = set(user_text.split())
            overlap = len(ref_words.intersection(user_words))
            total = len(ref_words.union(user_words))
            return overlap / total if total > 0 else 0.0
    
    elif exercise.exercise_type in ['listen', 'speak']:
        # For audio exercises, return a placeholder score
        # In production, this would use speech-to-text and comparison
        return 0.8  # Placeholder
    
    return 0.0


def get_next_exercise(current_exercise):
    """Get the next exercise in the lesson"""
    next_exercise = Exercise.objects.filter(
        lesson=current_exercise.lesson,
        order__gt=current_exercise.order
    ).order_by('order').first()
    
    if next_exercise:
        return {
            'id': next_exercise.id,
            'type': next_exercise.exercise_type,
            'prompt': next_exercise.prompt,
        }
    return None


@login_required
def milestone_challenge(request, level_id):
    """Milestone recording challenge"""
    level = get_object_or_404(Level, id=level_id)
    milestone = get_object_or_404(MilestoneChallenge, level=level)
    
    # Get user's previous attempts
    attempts = MilestoneAttempt.objects.filter(
        user=request.user,
        milestone=milestone
    ).order_by('-created_at')
    
    context = {
        'level': level,
        'milestone': milestone,
        'attempts': attempts,
    }
    
    return render(request, 'myApp/milestone_challenge.html', context)


@login_required
@require_http_methods(["POST"])
def submit_milestone(request, milestone_id):
    """Submit milestone attempt"""
    milestone = get_object_or_404(MilestoneChallenge, id=milestone_id)
    user = request.user
    
    try:
        data = json.loads(request.body)
        audio_recording = data.get('audio_recording', '')
        duration_seconds = data.get('duration', 0)
        
        # Calculate rubric scores (placeholder - in production, use AI)
        rubric_scores = {
            'clarity': 0.8,
            'structure': 0.7,
            'presence': 0.9,
            'influence': 0.6,
        }
        
        # Calculate overall score
        weights = milestone.rubric.get('weights', {
            'clarity': 0.3,
            'structure': 0.3,
            'presence': 0.2,
            'influence': 0.2,
        })
        
        overall_score = sum(rubric_scores[key] * weights.get(key, 0.25) 
                          for key in rubric_scores.keys())
        
        is_passed = overall_score >= 0.7  # 70% threshold
        
        # Calculate rewards
        xp_earned = milestone.xp_reward if is_passed else milestone.xp_reward // 2
        coins_earned = milestone.coins_reward if is_passed else 0
        
        # Create attempt
        attempt = MilestoneAttempt.objects.create(
            user=user,
            milestone=milestone,
            audio_recording=audio_recording,
            duration_seconds=duration_seconds,
            is_passed=is_passed,
            overall_score=overall_score,
            rubric_scores=rubric_scores,
            xp_earned=xp_earned,
            coins_earned=coins_earned
        )
        
        # Update user progress
        if is_passed:
            profile = user.profile
            profile.total_xp += xp_earned
            profile.coins += coins_earned
            profile.current_level = min(profile.current_level + 1, 6)
            profile.save()
            
            # Unlock next level
            unlock_next_level(user)
        
        return JsonResponse({
            'success': True,
            'is_passed': is_passed,
            'overall_score': overall_score,
            'rubric_scores': rubric_scores,
            'xp_earned': xp_earned,
            'coins_earned': coins_earned,
        })
        
    except Exception as e:
        logger.error(f"Error submitting milestone: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def streak_page(request):
    """User streak and progress page"""
    try:
        streak = Streak.objects.get(user=request.user)
    except Streak.DoesNotExist:
        streak = Streak.objects.create(user=request.user)
    
    # Get recent activity
    recent_attempts = ExerciseAttempt.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'streak': streak,
        'recent_attempts': recent_attempts,
    }
    
    return render(request, 'myApp/streak_page.html', context)


@login_required
def leaderboard(request):
    """Leaderboard page"""
    entries = LeaderboardEntry.objects.all()[:50]  # Top 50
    
    # Get user's position
    try:
        user_entry = LeaderboardEntry.objects.get(user=request.user)
    except LeaderboardEntry.DoesNotExist:
        user_entry = None
    
    context = {
        'entries': entries,
        'user_entry': user_entry,
    }
    
    return render(request, 'myApp/leaderboard.html', context)


@login_required
def quests(request):
    """Quests and challenges page"""
    active_quests = Quest.objects.filter(is_active=True)
    user_quests = UserQuest.objects.filter(
        user=request.user,
        quest__in=active_quests
    )
    
    context = {
        'active_quests': active_quests,
        'user_quests': user_quests,
    }
    
    return render(request, 'myApp/quests.html', context)


@login_required
@require_http_methods(["POST"])
def start_quest(request, quest_id):
    """Start a quest for the user"""
    quest = get_object_or_404(Quest, id=quest_id, is_active=True)
    user = request.user
    
    # Check if user already has this quest
    user_quest, created = UserQuest.objects.get_or_create(
        user=user,
        quest=quest,
        defaults={
            'progress': {},
            'is_completed': False
        }
    )
    
    if created:
        messages.success(request, f'Started quest: {quest.name}')
    else:
        if user_quest.is_completed:
            messages.info(request, f'Quest "{quest.name}" is already completed!')
        else:
            messages.info(request, f'Quest "{quest.name}" is already in progress!')
    
    return redirect('quests')


@login_required
def complete_quest(request, quest_id):
    """Complete a quest and give rewards"""
    quest = get_object_or_404(Quest, id=quest_id)
    user = request.user
    
    try:
        user_quest = UserQuest.objects.get(user=user, quest=quest)
        
        if not user_quest.is_completed:
            # Mark as completed
            user_quest.is_completed = True
            user_quest.completed_at = timezone.now()
            user_quest.save()
            
            # Give rewards
            profile = user.profile
            profile.total_xp += quest.xp_reward
            profile.coins += quest.coins_reward
            profile.gems += quest.gems_reward
            profile.save()
            
            messages.success(request, f'Quest completed! Earned {quest.xp_reward} XP and {quest.coins_reward} coins!')
        else:
            messages.info(request, 'Quest already completed!')
            
    except UserQuest.DoesNotExist:
        messages.error(request, 'Quest not found!')
    
    return redirect('quests')


def update_user_streak(user):
    """Update user's streak based on activity"""
    try:
        streak = Streak.objects.get(user=user)
    except Streak.DoesNotExist:
        streak = Streak.objects.create(user=user)
    
    now = timezone.now()
    last_activity = streak.last_activity
    
    if last_activity:
        # Check if it's been more than 24 hours since last activity
        time_diff = now - last_activity
        if time_diff.days >= 2:  # More than 1 day gap, reset streak
            streak.current_streak = 1
        elif time_diff.days == 1:  # Exactly 1 day, increment streak
            streak.current_streak += 1
        # If same day, don't change streak
    else:
        # First activity
        streak.current_streak = 1
    
    streak.last_activity = now
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.save()
    
    # Update profile
    profile = user.profile
    profile.current_streak = streak.current_streak
    profile.longest_streak = streak.longest_streak
    profile.last_activity = now
    profile.save()


def levels_view(request):
    """All levels page"""
    levels = Level.objects.all().order_by('number')
    
    context = {
        'levels': levels,
    }
    
    return render(request, 'myApp/levels.html', context)


@login_required
def profile_view(request):
    """User profile page"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Get user's recent activity
    recent_attempts = ExerciseAttempt.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Get user's rewards
    user_rewards = UserReward.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'recent_attempts': recent_attempts,
        'user_rewards': user_rewards,
    }
    
    return render(request, 'myApp/profile.html', context)


def unlock_next_level(user):
    """Unlock next level and create rewards"""
    profile = user.profile
    
    # Create level completion rewards
    level_rewards = [
        {'name': f'Level {profile.current_level} Master', 'type': 'badge'},
        {'name': f'Level {profile.current_level} Coins', 'type': 'coin', 'quantity': 50},
    ]
    
    for reward_data in level_rewards:
        reward, created = Reward.objects.get_or_create(
            name=reward_data['name'],
            defaults={
                'reward_type': reward_data['type'],
                'description': f'Reward for completing Level {profile.current_level}',
                'level_required': profile.current_level,
            }
        )
        
        if created or not UserReward.objects.filter(user=user, reward=reward).exists():
            UserReward.objects.create(
                user=user,
                reward=reward,
                quantity=reward_data.get('quantity', 1)
            )
