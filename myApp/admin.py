from django.contrib import admin
from .models import (
    Profile, AuthProvider, Level, Unit, Lesson, Exercise, ExerciseAttempt,
    MilestoneChallenge, MilestoneAttempt, TipSheet, District, Reward,
    UserReward, Streak, Quest, UserQuest, LeaderboardEntry,
    SubscriptionPlan, Subscription, ContentBlock
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_level', 'total_xp', 'current_streak', 'coins', 'gems']
    list_filter = ['current_level', 'learning_goal']
    search_fields = ['user__username', 'user__email']


@admin.register(AuthProvider)
class AuthProviderAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'provider_id', 'created_at']
    list_filter = ['provider', 'created_at']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'duration_minutes', 'xp_required', 'district_name']
    list_filter = ['number']
    ordering = ['number']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'order', 'duration_minutes']
    list_filter = ['level']
    ordering = ['level', 'order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'order', 'duration_minutes', 'xp_reward']
    list_filter = ['unit__level']
    ordering = ['unit__level', 'unit__order', 'order']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'exercise_type', 'order', 'xp_reward']
    list_filter = ['exercise_type', 'lesson__unit__level']
    ordering = ['lesson__unit__level', 'lesson__unit__order', 'lesson__order', 'order']


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'attempt_number', 'is_correct', 'score', 'xp_earned', 'created_at']
    list_filter = ['is_correct', 'exercise__exercise_type', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(MilestoneChallenge)
class MilestoneChallengeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'duration_seconds', 'xp_reward', 'coins_reward']
    list_filter = ['level']


@admin.register(MilestoneAttempt)
class MilestoneAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'milestone', 'is_passed', 'overall_score', 'xp_earned', 'created_at']
    list_filter = ['is_passed', 'milestone__level', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(TipSheet)
class TipSheetAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson']
    list_filter = ['lesson__unit__level']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'coach_name', 'xp_required']
    list_filter = ['level']


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'reward_type', 'level_required', 'xp_required']
    list_filter = ['reward_type', 'level_required']


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'quantity', 'earned_at']
    list_filter = ['reward__reward_type', 'earned_at']
    search_fields = ['user__username', 'user__email']


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity']
    search_fields = ['user__username', 'user__email']


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'quest_type', 'xp_reward', 'coins_reward', 'is_active']
    list_filter = ['quest_type', 'is_active']


@admin.register(UserQuest)
class UserQuestAdmin(admin.ModelAdmin):
    list_display = ['user', 'quest', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'quest__quest_type']
    search_fields = ['user__username', 'user__email']


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'rank', 'total_xp', 'current_streak', 'league', 'updated_at']
    list_filter = ['league', 'updated_at']
    search_fields = ['user__username', 'user__email']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly', 'price_yearly', 'max_family_members', 'is_active']
    list_filter = ['is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'is_active', 'started_at', 'expires_at']
    list_filter = ['is_active', 'plan', 'started_at']
    search_fields = ['user__username', 'user__email']


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'order', 'lesson', 'exercise']
    list_filter = ['content_type', 'lesson__unit__level']
    ordering = ['order']
