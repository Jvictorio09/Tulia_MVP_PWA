from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Profile(models.Model):
    """Extended user profile with learning preferences and progress"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Learning preferences
    daily_goal_minutes = models.IntegerField(default=5, validators=[MinValueValidator(2), MaxValueValidator(60)])
    learning_goal = models.CharField(max_length=100, default="converse_confidently")
    
    # Progress tracking
    current_level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(6)])
    total_xp = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Rewards (simplified: XP + Coins + Tickets only)
    coins = models.IntegerField(default=0)
    tickets = models.IntegerField(default=0)  # For district venue entry
    
    # Personalization (from onboarding)
    persona = models.JSONField(default=dict, blank=True)  # Role, audience, goal, etc.
    contexts = models.JSONField(default=list, blank=True)  # Typical speaking contexts
    goals = models.JSONField(default=list, blank=True)  # Learning goals
    
    # A/B testing
    ab_variant = models.CharField(max_length=1, default='A', choices=[('A', 'Dashboard-first'), ('B', 'Map-first')])
    
    # Onboarding status
    onboarding_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - Level {self.current_level}"


class AuthProvider(models.Model):
    """Social authentication providers"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)  # google, apple, facebook
    provider_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Level(models.Model):
    """Learning levels (1-6) with progression gates"""
    number = models.IntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField()  # Total estimated time
    xp_required = models.IntegerField()  # XP needed to unlock
    milestone_duration_seconds = models.IntegerField()  # Milestone recording time
    
    # Unlock rule (e.g., "must_pass_milestone", "complete_modules_a_d")
    unlock_rule = models.CharField(
        max_length=50,
        default="complete_previous_level",
        help_text="Rule for unlocking this level (e.g., 'must_pass_milestone', 'complete_modules_a_d')"
    )
    
    # Speakopoly district
    district_name = models.CharField(max_length=100)
    district_description = models.TextField()
    district_image = models.URLField(blank=True)
    
    # Rewards for completing level
    coins_reward = models.IntegerField(default=0)
    tickets_reward = models.IntegerField(default=0)  # Replaces gems_reward
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"Level {self.number}: {self.name}"


class Unit(models.Model):
    """Units within levels (e.g., 'Awareness & Foundations')"""
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()
    duration_minutes = models.IntegerField()
    
    class Meta:
        ordering = ['level', 'order']
        unique_together = ['level', 'order']
    
    def __str__(self):
        return f"{self.level.name} - {self.name}"


class Lesson(models.Model):
    """Individual lessons (5-10 minutes each)"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()
    duration_minutes = models.IntegerField()
    xp_reward = models.IntegerField(default=10)
    
    # Content
    tip_sheet = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True)
    
    class Meta:
        ordering = ['unit', 'order']
        unique_together = ['unit', 'order']
    
    def __str__(self):
        return f"{self.unit.name} - {self.name}"


class Exercise(models.Model):
    """Individual exercises within lessons"""
    EXERCISE_TYPES = [
        ('select', 'Single/Multi Select'),
        ('match', 'Match/Order'),
        ('rewrite', 'Rewrite for Clarity'),
        ('listen', 'Tap What You Hear'),
        ('speak', 'Say It Aloud'),
        ('scenario', 'Scenario Choice'),
        ('milestone', 'Milestone Recording'),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    order = models.IntegerField()
    
    # Content
    prompt = models.TextField()
    stimulus_text = models.TextField(blank=True)
    stimulus_audio = models.URLField(blank=True)
    stimulus_image = models.URLField(blank=True)
    
    # For select/match exercises
    options = models.JSONField(default=list, blank=True)  # List of options
    correct_answers = models.JSONField(default=list)  # List of correct answer indices/values
    
    # For rewrite exercises
    reference_rewrite = models.TextField(blank=True)
    
    # For milestone exercises
    rubric_criteria = models.JSONField(default=dict, blank=True)  # Scoring criteria
    
    # Knowledge Block references (which Knowledge Blocks were used to generate this exercise)
    concept_refs = models.JSONField(default=list, blank=True, help_text="List of KnowledgeBlock slugs used")
    
    # Scoring
    xp_reward = models.IntegerField(default=5)
    max_attempts = models.IntegerField(default=3)
    
    # Hints and feedback
    hints = models.TextField(blank=True)
    feedback_correct = models.TextField(blank=True)
    feedback_incorrect = models.TextField(blank=True)
    
    class Meta:
        ordering = ['lesson', 'order']
        unique_together = ['lesson', 'order']
    
    def __str__(self):
        return f"{self.lesson.name} - {self.get_exercise_type_display()}"


class ExerciseAttempt(models.Model):
    """User attempts at exercises"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    attempt_number = models.IntegerField(default=1)
    
    # Response data
    user_response = models.JSONField()  # User's answer(s)
    audio_recording = models.URLField(blank=True)  # For speak/milestone exercises
    duration_seconds = models.IntegerField()
    
    # Scoring
    is_correct = models.BooleanField()
    score = models.FloatField()  # 0.0 to 1.0
    xp_earned = models.IntegerField()
    
    # AI/ML feedback (for future enhancement)
    ai_feedback = models.TextField(blank=True)
    rubric_scores = models.JSONField(default=dict, blank=True)  # For milestone exercises
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise} (Attempt {self.attempt_number})"


class MilestoneChallenge(models.Model):
    """Milestone recording challenges for each level"""
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_seconds = models.IntegerField()
    
    # Rubric for scoring
    rubric = models.JSONField(default=dict)  # Criteria and weights
    
    # Rewards
    xp_reward = models.IntegerField(default=50)
    coins_reward = models.IntegerField(default=20)
    
    def __str__(self):
        return f"{self.level.name} - {self.name}"


class MilestoneAttempt(models.Model):
    """User attempts at milestone challenges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    milestone = models.ForeignKey(MilestoneChallenge, on_delete=models.CASCADE)
    
    # Recording
    audio_recording = models.URLField()
    duration_seconds = models.IntegerField()
    
    # Scoring
    is_passed = models.BooleanField()
    overall_score = models.FloatField()  # 0.0 to 1.0
    rubric_scores = models.JSONField()  # Individual criteria scores
    ai_feedback = models.TextField(blank=True)
    
    # Rewards
    xp_earned = models.IntegerField()
    coins_earned = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.milestone.name}"


class TipSheet(models.Model):
    """Tip sheets for lessons"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='tip_sheet_obj')
    title = models.CharField(max_length=100)
    content = models.TextField()
    examples = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Tips for {self.lesson.name}"


class District(models.Model):
    """Speakopoly districts/venues (2D elegant map)"""
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(blank=True)
    coach_name = models.CharField(max_length=100, blank=True)
    coach_description = models.TextField(blank=True)
    
    # Unlock requirements
    xp_required = models.IntegerField()
    
    # Ticket cost per venue (for entry into venues within this district)
    ticket_cost_per_venue = models.IntegerField(default=1, help_text="Tickets required to enter each venue in this district")
    
    def __str__(self):
        return f"{self.level.name} - {self.name}"


class Reward(models.Model):
    """Rewards and badges"""
    REWARD_TYPES = [
        ('coin', 'Coin'),
        ('gem', 'Gem'),
        ('badge', 'Badge'),
        ('token', 'Token'),
    ]
    
    name = models.CharField(max_length=100)
    reward_type = models.CharField(max_length=10, choices=REWARD_TYPES)
    description = models.TextField()
    icon = models.URLField(blank=True)
    
    # Unlock requirements
    level_required = models.IntegerField(null=True, blank=True)
    xp_required = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class UserReward(models.Model):
    """User's earned rewards"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['user', 'reward']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"


class Streak(models.Model):
    """User streak tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    streak_freeze_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"


class Quest(models.Model):
    """Daily quests only (simplified)"""
    QUEST_TYPES = [
        ('daily', 'Daily Quest'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    quest_type = models.CharField(max_length=10, choices=QUEST_TYPES, default='daily')
    
    # Requirements
    xp_required = models.IntegerField(null=True, blank=True)
    lessons_required = models.IntegerField(null=True, blank=True)
    streak_required = models.IntegerField(null=True, blank=True)
    
    # Rewards (simplified: no gems)
    xp_reward = models.IntegerField(default=0)
    coins_reward = models.IntegerField(default=0)
    
    # Timing
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class UserQuest(models.Model):
    """User quest progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    progress = models.JSONField(default=dict)  # Track specific requirements
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'quest']
    
    def __str__(self):
        return f"{self.user.username} - {self.quest.name}"


class LeaderboardEntry(models.Model):
    """Leaderboard entries (unlocked after N lessons)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_xp = models.IntegerField()
    current_streak = models.IntegerField()
    lessons_completed = models.IntegerField()
    rank = models.IntegerField()
    
    # League system
    league = models.CharField(max_length=20, default='bronze')  # bronze, silver, gold, diamond
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_xp', '-current_streak']
    
    def __str__(self):
        return f"{self.user.username} - Rank {self.rank}"


class SubscriptionPlan(models.Model):
    """Subscription plans"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Features
    features = models.JSONField(default=list)
    max_family_members = models.IntegerField(default=1)
    
    # Stripe integration
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """User subscriptions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Family plan
    family_members = models.ManyToManyField(User, related_name='family_subscription', blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"


class ContentBlock(models.Model):
    """Rich content blocks for CMS-like editing"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_type = models.CharField(max_length=50)  # text, image, video, audio
    order = models.IntegerField(default=0)
    
    # Associated with lessons or exercises
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='content_blocks')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True, blank=True, related_name='content_blocks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class KnowledgeBlock(models.Model):
    """
    Knowledge Blocks seeded from Level-1 Modules A-D (Foundations, Audience, Style, Clarity)
    Used by n8n/RAG to generate lesson content dynamically
    """
    slug = models.SlugField(unique=True, max_length=200, help_text="Unique identifier (e.g., 'signal-sentence', '3x3-message-builder')")
    summary = models.TextField(help_text="Brief summary of the concept (≤120 words)")
    tags = models.JSONField(default=list, blank=True, help_text="Tags for categorization and retrieval")
    exercise_seeds = models.JSONField(default=list, blank=True, help_text="Example exercise prompts/templates")
    citations = models.JSONField(
        default=list,
        blank=True,
        help_text="Source citations (e.g., [{'module': 'Module A - Foundations', 'section': 'Signal Sentence'}])"
    )
    
    # Module reference (A, B, C, D)
    module = models.CharField(
        max_length=1,
        choices=[('A', 'Module A - Foundations'), ('B', 'Module B - Audience'), ('C', 'Module C - Style'), ('D', 'Module D - Clarity')],
        help_text="Which Level-1 module this knowledge block belongs to"
    )
    
    # Content authority
    content = models.TextField(help_text="Full content/explanation of the concept")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['module', 'slug']
    
    def __str__(self):
        return f"{self.get_module_display()} - {self.slug}"
