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
]
