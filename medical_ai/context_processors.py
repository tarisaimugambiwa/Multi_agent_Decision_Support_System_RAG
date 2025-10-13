"""
Context processors for making session and user data available globally in templates.
"""

def user_session_data(request):
    """
    Add user session data to all template contexts.
    This makes role information and session data available without explicit passing.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Basic user info
        context['user_role'] = request.user.role
        context['is_nurse'] = request.user.role == 'NURSE'
        context['is_doctor'] = request.user.role == 'DOCTOR'
        context['is_expert'] = request.user.role == 'EXPERT'
        
        # Session data
        context['user_fullname'] = request.user.get_full_name() or request.user.username
        context['user_display_name'] = request.user.first_name or request.user.username
        
        # Dashboard URL based on role
        dashboard_urls = {
            'NURSE': 'nurse_dashboard',
            'DOCTOR': 'doctor_dashboard',
            'EXPERT': 'expert_dashboard'
        }
        context['user_dashboard'] = dashboard_urls.get(request.user.role, 'home')
        
        # Role-specific permissions
        context['can_create_cases'] = request.user.role in ['NURSE', 'DOCTOR', 'EXPERT']
        context['can_review_cases'] = request.user.role in ['DOCTOR', 'EXPERT']
        context['can_upload_documents'] = request.user.role in ['DOCTOR', 'EXPERT'] or request.user.is_staff
        context['can_manage_system'] = request.user.role == 'EXPERT' or request.user.is_staff
        
    return context
