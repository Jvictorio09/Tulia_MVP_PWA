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
from django.conf import settings
import json
import logging
import os

from .models import (
    Profile, Level, Unit, Lesson, Exercise, ExerciseAttempt,
    MilestoneChallenge, MilestoneAttempt, District, Reward,
    UserReward, Streak, Quest, UserQuest, LeaderboardEntry,
    SubscriptionPlan, Subscription, ContentBlock, KnowledgeBlock
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
            # Track signup completion via session flag for client-side tracking
            request.session['signup_completed'] = True
            return redirect('home')
    
    return render(request, 'myApp/auth/signup.html')


def logout_view(request):
    """Simple logout view"""
    logout(request)
    return redirect('home')


def login_redirect(request):
    """Redirect to login page with proper messaging"""
    messages.info(request, 'Please log in to access this page.')
    return redirect('login')


def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, 'myApp/404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'myApp/500.html', status=500)


def home(request):
    """Home page - landing for non-auth, dashboard for auth (A/B variants)"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        
        # Check if onboarding is needed
        if not profile.onboarding_completed:
            return redirect('onboarding')
        
        # Assign A/B variant if not set (50/50 split)
        if not profile.ab_variant:
            import random
            profile.ab_variant = 'A' if random.random() < 0.5 else 'B'
            profile.save()
        
        # Get user's current level and available districts
        current_level = profile.current_level
        level_1 = Level.objects.filter(number=1).first()
        districts = District.objects.filter(level=level_1) if level_1 else District.objects.none()
        
        # Get Level-1 modules (Units A-D)
        level_1_modules = Unit.objects.filter(level__number=1).order_by('order')[:4] if level_1 else []
        
        # Get user's active daily quests
        active_quests = Quest.objects.filter(is_active=True, quest_type='daily')
        user_quests = UserQuest.objects.filter(user=request.user, quest__in=active_quests)
        
        # Check if District-1 is unlocked (Level-1 milestone passed)
        district_1_unlocked = False
        if level_1:
            milestone = MilestoneChallenge.objects.filter(level=level_1).first()
            if milestone:
                passed = MilestoneAttempt.objects.filter(
                    user=request.user,
                    milestone=milestone,
                    is_passed=True
                ).exists()
                district_1_unlocked = passed
        
        # Check for signup completion flag
        signup_completed = request.session.pop('signup_completed', False)
        
        context = {
            'profile': profile,
            'level_1': level_1,
            'level_1_modules': level_1_modules,
            'districts': districts,
            'district_1_unlocked': district_1_unlocked,
            'user_quests': user_quests,
            'signup_completed': signup_completed,
        }
        return render(request, 'myApp/home.html', context)
    else:
        # New landing page for non-authenticated users
        return render(request, 'myApp/landing/index.html')


@login_required
def lesson_runner(request, lesson_id):
    """Interactive lesson runner with 3-zone layout (left rail, center, right AI Coach)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    exercises = lesson.exercises.all().order_by('order')
    
    # Get user's progress for this lesson
    completed_exercises = ExerciseAttempt.objects.filter(
        user=request.user,
        exercise__lesson=lesson,
        is_correct=True
    ).values_list('exercise_id', flat=True)
    
    # Check if this is user's first lesson (track for analytics)
    total_attempts = ExerciseAttempt.objects.filter(user=request.user).count()
    is_first_lesson = total_attempts == 0
    
    # Get Speakopoly district and level info
    level = lesson.unit.level if lesson.unit else None
    district = District.objects.filter(level=level).first() if level else None
    
    # Get module (A, B, C, D) from unit order
    module_letter = lesson.unit.name[0] if lesson.unit and lesson.unit.name else 'A'
    
    # Get Knowledge Blocks for this module (for AI Coach)
    knowledge_blocks = KnowledgeBlock.objects.filter(module=module_letter)[:5]
    
    # Get all units in this level for left rail outline
    all_units = Unit.objects.filter(level=level).order_by('order') if level else []
    
    context = {
        'lesson': lesson,
        'exercises': exercises,
        'completed_exercises': completed_exercises,
        'is_first_lesson': is_first_lesson,
        'level': level,
        'district': district,
        'module_letter': module_letter,
        'knowledge_blocks': knowledge_blocks,
        'all_units': all_units,
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
        
        # Calculate XP with streak multiplier (XP: 5-10 per exercise, streak multiplier ≤ 2×)
        profile = user.profile
        base_xp = min(max(exercise.xp_reward, 5), 10)  # Clamp between 5-10
        streak_multiplier = min(1.0 + (profile.current_streak * 0.1), 2.0)  # Max 2x multiplier
        xp_earned = int(base_xp * streak_multiplier)
        
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
    
    elif exercise.exercise_type == 'scenario':
        # For scenario exercises, same as select
        correct_answers = exercise.correct_answers
        if set(user_response) == set(correct_answers):
            return 1.0
        elif any(answer in correct_answers for answer in user_response):
            return 0.5  # Partial credit
        else:
            return 0.0
    
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
    """Submit milestone attempt (uses n8n scoring via ai_milestone_score endpoint)"""
    milestone = get_object_or_404(MilestoneChallenge, id=milestone_id)
    user = request.user
    
    try:
        data = json.loads(request.body)
        audio_recording = data.get('audio_recording', '')
        duration_seconds = data.get('duration_seconds', 0)
        rubric_scores = data.get('rubric_scores', {})
        overall_score = data.get('overall_score', 0.0)
        is_passed = data.get('is_passed', False)
        
        # Calculate rewards (Tickets: +3 for passing Milestone)
        xp_earned = milestone.xp_reward if is_passed else milestone.xp_reward // 2
        coins_earned = milestone.coins_reward if is_passed else 0
        tickets_earned = 3 if is_passed else 0  # +3 tickets for passing milestone
        
        # Create attempt
        attempt = MilestoneAttempt.objects.create(
            user=user,
            milestone=milestone,
            audio_recording=audio_recording,
            duration_seconds=duration_seconds,
            is_passed=is_passed,
            overall_score=overall_score,
            rubric_scores=rubric_scores,
            ai_feedback=data.get('coaching_note', ''),
            xp_earned=xp_earned,
            coins_earned=coins_earned
        )
        
        # Update user progress
        if is_passed:
            profile = user.profile
            profile.total_xp += xp_earned
            profile.coins += coins_earned
            profile.tickets += tickets_earned
            profile.save()
            
            # Unlock District-1 (Level-1 milestone passed)
            if milestone.level.number == 1:
                # District-1 is now unlocked
                pass
        
        return JsonResponse({
            'success': True,
            'is_passed': is_passed,
            'overall_score': overall_score,
            'rubric_scores': rubric_scores,
            'xp_earned': xp_earned,
            'coins_earned': coins_earned,
            'tickets_earned': tickets_earned,
            'district_unlocked': is_passed and milestone.level.number == 1,
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
            
            # Give rewards (simplified: no gems)
            profile = user.profile
            profile.total_xp += quest.xp_reward
            profile.coins += quest.coins_reward
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


@login_required
@require_http_methods(["POST"])
def complete_lesson(request, lesson_id):
    """Complete a lesson and unlock next level if applicable"""
    from django.http import JsonResponse
    import json
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user
    
    # Add lesson XP and coins (simplified economy)
    profile = user.profile
    profile.total_xp += lesson.xp_reward
    profile.coins += lesson.xp_reward // 2  # 1 coin per 2 XP
    
    # Award tickets for module completion (+1 per module)
    # Check if all lessons in the unit are completed
    unit = lesson.unit
    all_lessons = unit.lessons.all()
    completed_lessons = ExerciseAttempt.objects.filter(
        user=user,
        exercise__lesson__unit=unit,
        is_correct=True
    ).values_list('exercise__lesson_id', flat=True).distinct()
    
    if len(completed_lessons) >= all_lessons.count():
        # Module completed - award ticket
        profile.tickets += 1
    
    profile.save()
    
    # Check if we should unlock the next level
    current_level = lesson.unit.level
    next_level = None
    next_level_unlocked = False
    
    # Always unlock the next level when completing a lesson (progressive unlocking)
    next_level_obj = Level.objects.filter(number=current_level.number + 1).first()
    
    if next_level_obj and profile.current_level < next_level_obj.number:
        # Unlock the next level if not already unlocked
        profile.current_level = next_level_obj.number
        profile.save()
        next_level = next_level_obj.number
        next_level_unlocked = True
        
        # Give rewards for leveling up
        unlock_next_level(user)
    
    return JsonResponse({
        'success': True,
        'next_level_unlocked': next_level_unlocked,
        'next_level': next_level,
        'xp_earned': lesson.xp_reward,
    })


@login_required
def district_detail(request, level_id):
    """District-1 detail page (2D map)"""
    level = get_object_or_404(Level, id=level_id)
    districts = District.objects.filter(level=level)
    
    # Check if unlocked
    milestone = MilestoneChallenge.objects.filter(level=level).first()
    is_unlocked = False
    if milestone:
        is_unlocked = MilestoneAttempt.objects.filter(
            user=request.user,
            milestone=milestone,
            is_passed=True
        ).exists()
    
    context = {
        'level': level,
        'districts': districts,
        'is_unlocked': is_unlocked,
    }
    return render(request, 'myApp/district_detail.html', context)


@login_required
def district_venue(request, district_id):
    """District venue entry (ticket-gated)"""
    district = get_object_or_404(District, id=district_id)
    profile = request.user.profile
    
    # Check if user has enough tickets
    if profile.tickets < district.ticket_cost_per_venue:
        messages.error(request, f'You need {district.ticket_cost_per_venue} ticket(s) to enter this venue.')
        return redirect('district_detail', level_id=district.level.id)
    
    # Deduct tickets
    if request.method == 'POST':
        profile.tickets -= district.ticket_cost_per_venue
        profile.save()
        messages.success(request, f'Entered {district.name}!')
    
    context = {
        'district': district,
        'tickets_remaining': profile.tickets - district.ticket_cost_per_venue,
    }
    return render(request, 'myApp/district_venue.html', context)


@login_required
def onboarding(request):
    """First-run personalization flow (7 fast cards)"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Collect onboarding data
        persona = {
            'role': request.POST.get('role', ''),
            'typical_audience': request.POST.get('typical_audience', ''),
            'main_goal': request.POST.get('main_goal', ''),
            'comfort_under_pressure': request.POST.get('comfort_under_pressure', ''),
            'time_pressure_profile': request.POST.get('time_pressure_profile', ''),
            'preferred_practice_time': request.POST.get('preferred_practice_time', ''),
            'daily_goal': request.POST.get('daily_goal', '5'),
        }
        
        profile.persona = persona
        profile.contexts = request.POST.getlist('contexts', [])
        profile.goals = request.POST.getlist('goals', [])
        profile.daily_goal_minutes = int(request.POST.get('daily_goal', 5))
        profile.onboarding_completed = True
        profile.save()
        
        return redirect('home')
    
    return render(request, 'myApp/onboarding.html')


@login_required
def ai_chat(request):
    """AI Chat assistant page for lesson help"""
    try:
        profile = request.user.profile
        current_level = profile.current_level
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        current_level = 1
    
    # Get user's current lesson context
    context = {
        'profile': profile,
        'current_level': current_level,
    }
    
    return render(request, 'myApp/ai_chat.html', context)


@login_required
@require_http_methods(["POST"])
def send_ai_message(request):
    """Send message to AI webhook and get response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        # Import requests library
        try:
            import requests
        except ImportError:
            return JsonResponse({'success': False, 'error': 'requests library not installed. Run: pip install requests'}, status=500)
        
        # Get user context
        profile = request.user.profile
        current_level = profile.current_level
        
        # Webhook URL - can be overridden via environment variable
        webhook_url = os.getenv('AI_CHAT_WEBHOOK_URL', "https://speak-pro-app.fly.dev/webhook/9527da75-7725-439b-9bce-920dcac70acb")
        
        # Prepare payload with user context
        payload = {
            "message": user_message,
            "user_context": {
                "level": current_level,
                "total_xp": profile.total_xp,
                "current_streak": profile.current_streak,
                "username": request.user.username,
            }
        }
        
        # Call webhook
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                # If response is not JSON, try to get text
                ai_response = response.text.strip()
                if not ai_response:
                    raise ValueError("Empty response from webhook")
            else:
                # Handle different response formats
                if isinstance(response_data, dict):
                    # Try common response field names in order of likelihood
                    ai_response = (
                        response_data.get('response') or 
                        response_data.get('message') or 
                        response_data.get('text') or 
                        response_data.get('answer') or
                        response_data.get('content') or
                        response_data.get('output')
                    )
                    if not ai_response and 'choices' in response_data:
                        # Handle OpenAI-style response format
                        if isinstance(response_data['choices'], list) and len(response_data['choices']) > 0:
                            choice = response_data['choices'][0]
                            ai_response = choice.get('message', {}).get('content') or choice.get('text') or str(choice)
                    # If still no response, try to get the first string value
                    if not ai_response:
                        for key, value in response_data.items():
                            if isinstance(value, str) and value.strip():
                                ai_response = value
                                break
                elif isinstance(response_data, str):
                    ai_response = response_data
                elif isinstance(response_data, list) and len(response_data) > 0:
                    # Handle list responses
                    ai_response = str(response_data[0])
                else:
                    ai_response = str(response_data)
            
            if not ai_response or not ai_response.strip():
                logger.warning(f"Unexpected or empty webhook response: {response_data if 'response_data' in locals() else response.text}")
                ai_response = "I received your message, but couldn't process the response. Please try again."
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
            })
            
        except requests.exceptions.Timeout:
            logger.error("Webhook request timed out")
            return JsonResponse({'success': False, 'error': 'Request timed out. Please try again.'}, status=504)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Webhook HTTP error: {e.response.status_code} - {e.response.text}")
            return JsonResponse({'success': False, 'error': f'AI service error (HTTP {e.response.status_code}). Please try again.'}, status=500)
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook request error: {e}")
            return JsonResponse({'success': False, 'error': f'Failed to connect to AI service. Please check your connection and try again.'}, status=500)
        
    except Exception as e:
        logger.error(f"Error in send_ai_message: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_lesson_orchestrate(request):
    """
    POST /ai/lesson/orchestrate
    n8n webhook for lesson orchestration - returns Teach/Drill/Review/Checkpoint blocks
    """
    try:
        data = json.loads(request.body)
        user = request.user
        profile = user.profile
        
        # Get context from request
        module = data.get('module', 'A')  # A, B, C, D
        block_type = data.get('block_type', 'teach')  # teach, drill, review, checkpoint
        last_block = data.get('last_block')
        last_score = data.get('last_score')
        confusion_flags = data.get('confusion_flags', [])
        
        # Get n8n webhook URL from environment
        webhook_url = os.getenv('N8N_LESSON_WEBHOOK_URL', '')
        
        if not webhook_url:
            # Fallback: return cached Knowledge Block if available
            knowledge_blocks = KnowledgeBlock.objects.filter(module=module)[:1]
            if knowledge_blocks.exists():
                kb = knowledge_blocks.first()
                return JsonResponse({
                    'success': True,
                    'block': {
                        'type': 'teach',
                        'title': kb.slug.replace('-', ' ').title(),
                        'content': kb.summary[:120],
                        'source_chips': [{'module': kb.get_module_display(), 'section': kb.slug}],
                        'why_it_matters': 'This concept is fundamental to effective communication.',
                        'concept_refs': [kb.slug]
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'n8n webhook not configured'}, status=500)
        
        # Prepare payload for n8n
        payload = {
            'user': {
                'id': user.id,
                'level': profile.current_level,
                'module': module,
                'streak': profile.current_streak,
                'xp': profile.total_xp,
                'tickets': profile.tickets,
                'persona': profile.persona,
                'goals': profile.goals,
            },
            'context': {
                'block_type': block_type,
                'last_block': last_block,
                'last_score': last_score,
                'confusion_flags': confusion_flags,
            },
            'module_metadata': {
                'target_concepts': ['Signal sentence', '3×3 message builder'] if module == 'D' else [],
            }
        }
        
        # Call n8n webhook
        try:
            import requests
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except Exception as e:
            logger.error(f"n8n lesson orchestrate error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    except Exception as e:
        logger.error(f"Error in ai_lesson_orchestrate: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_coach_respond(request):
    """
    POST /ai/coach/respond
    n8n webhook for ad-hoc coach Q&A
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        user = request.user
        profile = user.profile
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        webhook_url = os.getenv('N8N_COACH_WEBHOOK_URL', '')
        
        if not webhook_url:
            return JsonResponse({
                'success': True,
                'response': 'I understand your question. Please configure the n8n coach webhook to enable full responses.',
                'suggested_drill': None
            })
        
        payload = {
            'user': {
                'id': user.id,
                'level': profile.current_level,
                'persona': profile.persona,
            },
            'message': user_message,
        }
        
        try:
            import requests
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except Exception as e:
            logger.error(f"n8n coach respond error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    except Exception as e:
        logger.error(f"Error in ai_coach_respond: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_milestone_score(request):
    """
    POST /ai/milestone/score
    n8n webhook for milestone evaluation (transcribe + rubric scoring)
    """
    try:
        data = json.loads(request.body)
        milestone_id = data.get('milestone_id')
        audio_url = data.get('audio_url')
        duration_seconds = data.get('duration_seconds', 0)
        user = request.user
        
        if not milestone_id or not audio_url:
            return JsonResponse({'success': False, 'error': 'milestone_id and audio_url required'}, status=400)
        
        milestone = get_object_or_404(MilestoneChallenge, id=milestone_id)
        
        webhook_url = os.getenv('N8N_MILESTONE_WEBHOOK_URL', '')
        
        if not webhook_url:
            # Fallback: basic scoring
            return JsonResponse({
                'success': True,
                'rubric_scores': {
                    'clarity': 0.75,
                    'structure': 0.70,
                    'presence': 0.80,
                    'influence': 0.65,
                },
                'overall_score': 0.725,
                'is_passed': True,
                'coaching_note': 'Good effort! Configure n8n webhook for detailed feedback.',
            })
        
        payload = {
            'user': {'id': user.id},
            'milestone_id': milestone_id,
            'audio_url': audio_url,
            'duration_seconds': duration_seconds,
            'rubric': milestone.rubric,
        }
        
        try:
            import requests
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for audio processing
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except Exception as e:
            logger.error(f"n8n milestone score error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    except Exception as e:
        logger.error(f"Error in ai_milestone_score: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def ai_eligibility_check(request):
    """
    POST /ai/eligibility/check
    n8n webhook for eligibility & ticket calculations (optional centralization)
    """
    try:
        data = json.loads(request.body)
        user = request.user
        profile = user.profile
        action = data.get('action')  # 'lesson_complete', 'milestone_pass', etc.
        
        # Default: Django calculates eligibility server-side
        # This endpoint can be used if rules are complex or need AI logic
        
        webhook_url = os.getenv('N8N_ELIGIBILITY_WEBHOOK_URL', '')
        
        if not webhook_url:
            # Fallback: Django logic
            tickets_delta = 0
            can_unlock = False
            
            if action == 'module_complete':
                tickets_delta = 1
            elif action == 'milestone_pass':
                tickets_delta = 3
                # Check if District-1 can unlock
                level_1 = Level.objects.filter(number=1).first()
                if level_1:
                    milestone = MilestoneChallenge.objects.filter(level=level_1).first()
                    if milestone:
                        passed = MilestoneAttempt.objects.filter(
                            user=user,
                            milestone=milestone,
                            is_passed=True
                        ).exists()
                        can_unlock = passed
            
            return JsonResponse({
                'success': True,
                'tickets_delta': tickets_delta,
                'can_unlock': can_unlock,
                'unlock_rule': level_1.unlock_rule if level_1 else None,
            })
        
        payload = {
            'user': {
                'id': user.id,
                'level': profile.current_level,
                'tickets': profile.tickets,
            },
            'action': action,
        }
        
        try:
            import requests
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return JsonResponse(response.json())
        except Exception as e:
            logger.error(f"n8n eligibility check error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    except Exception as e:
        logger.error(f"Error in ai_eligibility_check: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
