from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_redirect, name='login_redirect'),
    
    # Main app
    path('', views.home, name='home'),
    path('levels/', views.levels_view, name='levels'),
    path('profile/', views.profile_view, name='profile'),
    path('lesson/<int:lesson_id>/', views.lesson_runner, name='lesson_runner'),
    path('exercise/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercise/<int:exercise_id>/submit/', views.submit_exercise, name='submit_exercise'),
    path('milestone/<int:level_id>/', views.milestone_challenge, name='milestone_challenge'),
    path('milestone/<int:milestone_id>/submit/', views.submit_milestone, name='submit_milestone'),
    path('streak/', views.streak_page, name='streak_page'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('quests/', views.quests, name='quests'),
    path('quests/<int:quest_id>/start/', views.start_quest, name='start_quest'),
    path('quests/<int:quest_id>/complete/', views.complete_quest, name='complete_quest'),
    
    # Lesson completion
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    
    # Onboarding
    path('onboarding/', views.onboarding, name='onboarding'),
    
    # AI Chat
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('ai-chat/send/', views.send_ai_message, name='send_ai_message'),
    
    # n8n/RAG Webhooks
    path('ai/lesson/orchestrate/', views.ai_lesson_orchestrate, name='ai_lesson_orchestrate'),
    path('ai/coach/respond/', views.ai_coach_respond, name='ai_coach_respond'),
    path('ai/milestone/score/', views.ai_milestone_score, name='ai_milestone_score'),
    path('ai/eligibility/check/', views.ai_eligibility_check, name='ai_eligibility_check'),
    
    # District & Venues
    path('district/<int:level_id>/', views.district_detail, name='district_detail'),
    path('district/venue/<int:district_id>/', views.district_venue, name='district_venue'),
]
