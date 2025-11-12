"""
URL configuration for medical_ai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.conf.urls.static import static

# Import views for direct URL patterns
from patients.views import nurse_dashboard, doctor_dashboard
from patients.models import Patient
from diagnoses.models import Case
from knowledge.models import KnowledgeDocument


def home_view(request):
    """
    Enhanced dashboard view for the Medical AI System with real data.
    
    Important: This view redirects unauthenticated users to the app login page,
    NOT the Django admin login. This ensures users see the custom purple gradient
    login page with demo credentials.
    """
    
    # Redirect unauthenticated users to login page
    if not request.user.is_authenticated:
        return redirect('login')  # Goes to /accounts/login/ (app login)
    
    # Base statistics available to all users
    total_patients = Patient.objects.count()
    total_cases = Case.objects.count()
    total_knowledge_docs = KnowledgeDocument.objects.filter(is_active=True).count()
    
    # Recent cases (last 10)
    recent_cases = Case.objects.select_related('patient', 'nurse', 'doctor').order_by('-created_at')[:10]
    
    # Urgent cases
    urgent_cases = Case.objects.filter(
        priority__in=['URGENT', 'CRITICAL'],
        status__in=['PENDING', 'IN_PROGRESS', 'DOCTOR_REVIEW']
    ).select_related('patient')[:5]
    
    # Role-specific statistics
    active_cases = 0
    pending_reviews = 0
    
    if request.user.is_authenticated:
        if request.user.role == 'NURSE':
            # Nurse-specific stats
            active_cases = Case.objects.filter(
                nurse=request.user,
                status__in=['PENDING', 'IN_PROGRESS']
            ).count()
            pending_reviews = Case.objects.filter(
                nurse=request.user,
                status='DOCTOR_REVIEW'
            ).count()
        elif request.user.role == 'DOCTOR':
            # Doctor-specific stats
            active_cases = Case.objects.filter(
                doctor=request.user,
                status__in=['IN_PROGRESS', 'DOCTOR_REVIEW']
            ).count()
            pending_reviews = Case.objects.filter(
                status='DOCTOR_REVIEW'
            ).count()
        else:
            # General stats for other roles
            active_cases = Case.objects.filter(
                status__in=['PENDING', 'IN_PROGRESS', 'DOCTOR_REVIEW']
            ).count()
            pending_reviews = Case.objects.filter(
                status='DOCTOR_REVIEW'
            ).count()
    
    context = {
        'total_patients': total_patients,
        'active_cases': active_cases,
        'pending_reviews': pending_reviews,
        'knowledge_docs': total_knowledge_docs,
        'recent_cases': recent_cases,
        'urgent_cases': urgent_cases,
        'system_health': {
            'database': '✓',
            'ai_service': '✓'
        }
    }
    return render(request, 'home.html', context)


# Custom login redirect view
def login_redirect_view(request):
    """Redirect users based on their role after login."""
    if request.user.is_authenticated:
        if request.user.role == 'NURSE':
            return redirect('nurse_dashboard')
        elif request.user.role == 'DOCTOR':
            return redirect('doctor_dashboard')
        elif request.user.role == 'EXPERT':
            return redirect('expert_dashboard')
        else:
            return redirect('home')
    return redirect('login')


# Custom login view with role-based redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib import messages

class RoleBasedLoginView(BaseLoginView):
    """Custom login view with automatic role detection and session management"""
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """
        Automatically detect user role and set up session.
        No dropdown selection needed - role is determined by username/password.
        """
        user = form.get_user()
        
        # Call parent form_valid to log the user in
        response = super().form_valid(form)
        
        # Set up session with role information
        self.request.session['user_role'] = user.role
        self.request.session['user_fullname'] = user.get_full_name() or user.username
        self.request.session['is_nurse'] = user.role == 'NURSE'
        self.request.session['is_doctor'] = user.role == 'DOCTOR'
        self.request.session['is_expert'] = user.role == 'EXPERT'
        
        # Add success message with role-specific greeting
        role_greetings = {
            'NURSE': '👩‍⚕️ Welcome back, Nurse',
            'DOCTOR': '👨‍⚕️ Welcome back, Dr.',
            'EXPERT': '🔬 Welcome back, Expert'
        }
        greeting = role_greetings.get(user.role, 'Welcome back')
        messages.success(
            self.request,
            f"{greeting} {user.get_full_name() or user.username}! Your session is active."
        )
        
        return response
    
    def get_success_url(self):
        """Redirect to role-specific dashboard after successful login"""
        user = self.request.user
        if user.role == 'NURSE':
            return '/nurse-dashboard/'
        elif user.role == 'DOCTOR':
            return '/doctor-dashboard/'
        elif user.role == 'PATIENT':
            return '/patients/dashboard/'
        else:
            return '/'  # Expert and other roles go to home


urlpatterns = [
    # Root URL - redirect directly to login page
    path("", lambda request: redirect('login'), name="root"),
    
    # Home page - dashboard after login
    path("home/", home_view, name="home"),
    
    # Authentication URLs - Main app login (NOT admin login)
    path("accounts/", include([
        path("login/", RoleBasedLoginView.as_view(), name="login"),
        # Logout redirects to app login page (purple gradient with demo credentials)
        path("logout/", auth_views.LogoutView.as_view(
            next_page="/accounts/login/",  # App login, NOT /system-admin/
            http_method_names=['get', 'post']
        ), name="logout"),
        path("password_change/", auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url='/accounts/password_change/done/'
        ), name="password_change"),
        path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ), name="password_change_done"),
        path("password_reset/", auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url='/accounts/password_reset/done/'
        ), name="password_reset"),
        path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ), name="password_reset_done"),
        path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/accounts/reset/done/'
        ), name="password_reset_confirm"),
        path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ), name="password_reset_complete"),
    ]), {'namespace': 'accounts'}),
    
    # Role-specific dashboards
    path("nurse-dashboard/", nurse_dashboard, name="nurse_dashboard"),
    path("doctor-dashboard/", doctor_dashboard, name="doctor_dashboard"),
    
    # Patients app URLs
    path("patients/", include('patients.urls', namespace='patients')),
    
    # Users app URLs
    path("users/", include([
        # User management (you can create this later)
        # path("", include('users.urls', namespace='users')),
    ])),
    
    # Diagnoses app URLs
    path("diagnoses/", include('diagnoses.urls', namespace='diagnoses')),
    
    # Knowledge app URLs
    path("knowledge/", include('knowledge.urls', namespace='knowledge')),
    
    # API endpoints
    path("api/", include([
        path("patients/", include([
            path("search/", include('patients.urls')),  # Patient search API
        ])),
        # Add more API endpoints here as needed
    ])),
    
    # Django Admin interface - Separate from app login
    # Use /system-admin/ for admin access (more secure than /admin/)
    # Admin login is SEPARATE - uses Django's default admin login
    # App users (nurse/doctor) should use /accounts/login/ NOT /system-admin/
    path("system-admin/", admin.site.urls),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'assets')
