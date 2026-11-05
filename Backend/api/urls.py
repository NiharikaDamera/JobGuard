from django.urls import path

from .views import (
    analyze_job,
    analysis_history,
    analysis_detail,
    register_user,
    login_user
)

urlpatterns = [
    path('analyze/', analyze_job, name='analyze_job'),
    path('history/', analysis_history, name='analysis_history'),
    path('history/<int:analysis_id>/', analysis_detail, name='analysis_detail'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
]