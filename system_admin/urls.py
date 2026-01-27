from django.urls import path
from . import views

app_name = 'system_admin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('settings/', views.system_settings, name='settings'),
]
