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

# Import views for direct URL patterns
from patients.views import nurse_dashboard, doctor_dashboard
from patients.models import Patient
from diagnoses.models import Case
from knowledge.models import KnowledgeDocument


def home_view(request):
    """Enhanced dashboard view for the Medical AI System with real data."""
    
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
    """Custom login view that redirects based on user role and validates role selection"""
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Validate that the user has the selected role"""
        # Get the selected role from the form
        selected_role = self.request.POST.get('role', '').upper()
        user = form.get_user()
        
        # Check if user's role matches the selected role
        if selected_role and user.role != selected_role:
            # Add error message
            messages.error(
                self.request,
                f"Invalid credentials. Your account is not registered as a {selected_role.title()}. "
                f"Please select the correct role or contact your administrator."
            )
            return self.form_invalid(form)
        
        # If role matches or no role selected, proceed with login
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to role-specific dashboard after successful login"""
        user = self.request.user
        if user.role == 'NURSE':
            return '/nurse-dashboard/'
        elif user.role == 'DOCTOR':
            return '/doctor-dashboard/'
        elif user.role == 'EXPERT':
            return '/expert-dashboard/'
        else:
            return '/'


urlpatterns = [
    # Home page
    path("", home_view, name="home"),
    
    # Authentication URLs
    path("accounts/", include([
        path("login/", RoleBasedLoginView.as_view(), name="login"),
        path("logout/", auth_views.LogoutView.as_view(
            next_page="/accounts/login/",
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
    path("patients/", include([
        # Patient management
        path("", include('patients.urls', namespace='patients')),
    ])),
    
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
    
    # Admin interface
    path("admin/", admin.site.urls),
]
