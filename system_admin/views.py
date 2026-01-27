from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from users.models import User, Facility, UserProfile
from patients.models import Patient
from diagnoses.models import Case
from communications.models import Conversation, Message, Call


def is_superuser(user):
    """Check if user is a superuser"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """
    Main admin dashboard with system statistics and management overview
    """
    # User Statistics
    total_users = User.objects.count()
    nurses_count = User.objects.filter(role='NURSE').count()
    doctors_count = User.objects.filter(role='DOCTOR').count()
    patients_count = User.objects.filter(role='PATIENT').count()
    experts_count = User.objects.filter(role='EXPERT').count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Patient Statistics
    total_patients = Patient.objects.count()
    recent_patients = Patient.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Case/Diagnosis Statistics
    total_cases = Case.objects.count()
    pending_cases = Case.objects.filter(status='pending').count()
    reviewed_cases = Case.objects.filter(status='reviewed').count()
    urgent_cases = Case.objects.filter(priority='high').count()
    cases_today = Case.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    cases_this_week = Case.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    cases_this_month = Case.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Communication Statistics
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    unread_messages = Message.objects.filter(is_read=False).count()
    total_calls = Call.objects.count()
    voice_calls = Call.objects.filter(call_type='voice').count()
    video_calls = Call.objects.filter(call_type='video').count()
    missed_calls = Call.objects.filter(status='missed').count()
    
    # Facility Statistics
    total_facilities = Facility.objects.count()
    
    # Recent Activity
    recent_cases = Case.objects.select_related(
        'patient', 'nurse'
    ).order_by('-created_at')[:10]
    
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    recent_calls = Call.objects.select_related(
        'caller', 'receiver'
    ).order_by('-started_at')[:10]
    
    # System Health Metrics
    avg_case_response_time = None  # Can be calculated if timestamps are tracked
    
    context = {
        # User Stats
        'total_users': total_users,
        'nurses_count': nurses_count,
        'doctors_count': doctors_count,
        'patients_count': patients_count,
        'experts_count': experts_count,
        'active_users': active_users,
        
        # Patient Stats
        'total_patients': total_patients,
        'recent_patients': recent_patients,
        
        # Case Stats
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'reviewed_cases': reviewed_cases,
        'urgent_cases': urgent_cases,
        'cases_today': cases_today,
        'cases_this_week': cases_this_week,
        'cases_this_month': cases_this_month,
        
        # Communication Stats
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'total_calls': total_calls,
        'voice_calls': voice_calls,
        'video_calls': video_calls,
        'missed_calls': missed_calls,
        
        # Facility Stats
        'total_facilities': total_facilities,
        
        # Recent Activity
        'recent_cases': recent_cases,
        'recent_users': recent_users,
        'recent_calls': recent_calls,
    }
    
    return render(request, 'system_admin/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def user_management(request):
    """User management page"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if provided
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
    }
    return render(request, 'system_admin/user_management.html', context)


@login_required
@user_passes_test(is_superuser)
def system_settings(request):
    """System settings and configuration"""
    facilities = Facility.objects.all()
    
    context = {
        'facilities': facilities,
    }
    return render(request, 'system_admin/settings.html', context)
