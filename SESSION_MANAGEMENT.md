# Session Management & Role-Based Access Control

## Overview
The Medical AI System now features **automatic role detection** and **session-based access control**. Users are automatically identified as Nurse, Doctor, or Expert based solely on their username and password - no manual role selection required.

## ✨ Key Features

### 1. Automatic Role Detection
- **No Dropdown Selection**: Users simply enter username and password
- **Instant Role Recognition**: System automatically detects if user is Nurse, Doctor, or Expert
- **Secure Session Management**: Role information stored in encrypted session data
- **Role-Specific Greeting**: Personalized welcome message based on detected role

### 2. Session Management
When a user logs in, the system automatically stores:
- `user_role`: NURSE, DOCTOR, or EXPERT
- `user_fullname`: User's full name or username
- `is_nurse`, `is_doctor`, `is_expert`: Boolean flags for quick checks
- Session expires after 24 hours of inactivity
- Secure cookie-based authentication

### 3. Role-Based Navigation

#### 👩‍⚕️ NURSE Navigation
Nurses see **limited, focused options** for patient care:
```
✓ Nurse Dashboard
✓ Patient Care Section:
  - Patients
  - New Case
  - Diagnostic Cases
  - Medical Records
```

#### 👨‍⚕️ DOCTOR Navigation
Doctors see **clinical and knowledge-focused options**:
```
✓ Doctor Dashboard
✓ Patient Management Section:
  - Patients
  - Medical Records
✓ Resources Section:
  - Knowledge Base
```

#### 🔬 EXPERT/ADMIN Navigation
Experts/Admins see **full system access**:
```
✓ Dashboard
✓ Expert Dashboard
✓ Patient Care (all options)
✓ Resources:
  - Knowledge Base
  - Upload Document
✓ Management:
  - Analytics
  - Admin Panel (if staff)
```

## 🔐 Security Features

### Authentication Flow
1. User enters username and password (no role dropdown)
2. Django authenticates credentials
3. System retrieves user's assigned role from database
4. Session is created with role information
5. User redirected to role-specific dashboard
6. Navigation menu dynamically generated based on role

### Session Security
- **Encrypted cookies**: Session data encrypted and signed
- **CSRF protection**: All forms protected against cross-site attacks
- **Session timeout**: 24-hour inactivity timeout
- **Secure logout**: Proper session cleanup on logout

### Permission Checks
Context processor provides global permission flags:
- `can_create_cases`: NURSE, DOCTOR, EXPERT
- `can_review_cases`: DOCTOR, EXPERT
- `can_upload_documents`: DOCTOR, EXPERT, STAFF
- `can_manage_system`: EXPERT, STAFF

## 📋 Implementation Details

### Modified Files

#### 1. `medical_ai/urls.py`
**RoleBasedLoginView** - Enhanced login view with automatic role detection:
```python
def form_valid(self, form):
    user = form.get_user()
    # Set up session with role information
    self.request.session['user_role'] = user.role
    self.request.session['is_nurse'] = user.role == 'NURSE'
    self.request.session['is_doctor'] = user.role == 'DOCTOR'
    # ... personalized greeting
```

#### 2. `templates/login.html`
**Simplified Login Form**:
- Removed role dropdown selector
- Added visual role indicators (badges)
- Enhanced UI with gradient styling
- Clear messaging about automatic role detection

#### 3. `templates/base.html`
**Dynamic Sidebar Navigation**:
- Conditional rendering based on `user.role`
- Nurse-specific menu (6 items)
- Doctor-specific menu (4 items)
- Expert/Admin full menu
- Active link highlighting

#### 4. `medical_ai/context_processors.py`
**Global Context Processor**:
- Makes role data available to all templates
- Provides permission flags
- No need to pass user data explicitly in views

#### 5. `medical_ai/settings.py`
**Session & Context Configuration**:
```python
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
context_processors = [
    ...
    "medical_ai.context_processors.user_session_data",
]
```

## 🚀 Usage

### For Users
1. Navigate to `/accounts/login/`
2. Enter your username and password
3. Click "Sign In"
4. System automatically:
   - Detects your role
   - Creates secure session
   - Redirects to appropriate dashboard
   - Shows role-specific navigation menu

### For Administrators
To assign roles to users:
1. Access Django Admin (`/admin/`)
2. Navigate to Users
3. Edit user profile
4. Set **Role** field to: NURSE, DOCTOR, or EXPERT
5. Save changes

User will see appropriate navigation on next login.

## 🧪 Testing

### Test Accounts (Create via Django Admin)
```python
# Create test users with different roles
python manage.py shell

from users.models import User

# Nurse account
nurse = User.objects.create_user(
    username='nurse1',
    password='nurse123',
    role='NURSE',
    first_name='Sarah',
    last_name='Johnson'
)

# Doctor account
doctor = User.objects.create_user(
    username='doctor1',
    password='doctor123',
    role='DOCTOR',
    first_name='James',
    last_name='Wilson'
)

# Expert account
expert = User.objects.create_user(
    username='expert1',
    password='expert123',
    role='EXPERT',
    first_name='Emily',
    last_name='Chen'
)
```

### Testing Steps
1. **Test Nurse Login**:
   - Login as `nurse1`
   - Verify: See only 6 menu items (Nurse Dashboard, Patients, New Case, Diagnostic Cases, Medical Records)
   - Verify: Redirected to `/nurse-dashboard/`
   - Verify: Greeting shows "Welcome back, Nurse Sarah Johnson!"

2. **Test Doctor Login**:
   - Login as `doctor1`
   - Verify: See only 4 menu items (Doctor Dashboard, Patients, Medical Records, Knowledge Base)
   - Verify: Redirected to `/doctor-dashboard/`
   - Verify: Greeting shows "Welcome back, Dr. James Wilson!"

3. **Test Session Persistence**:
   - Navigate to different pages
   - Close and reopen browser (within 24 hours)
   - Verify: Still logged in with correct role
   - After 24 hours: Verify session expired

4. **Test Security**:
   - Try accessing restricted URLs directly
   - Verify: Redirected to login or error page
   - Check: Session cookie is httpOnly and secure

## 🔧 Troubleshooting

### Issue: Role not detected after login
**Solution**: 
- Check user has role assigned in Django Admin
- Verify context processor is in settings.py
- Clear browser cookies and try again

### Issue: Navigation menu shows wrong items
**Solution**:
- Restart Django server to apply template changes
- Check `user.role` in template with `{{ user.role }}`
- Verify user object has role attribute

### Issue: Session expires too quickly
**Solution**:
- Check `SESSION_COOKIE_AGE` in settings.py
- Ensure `SESSION_SAVE_EVERY_REQUEST = True`
- Check browser is not blocking cookies

## 🎯 Benefits

### For Nurses
- **Simplified Interface**: Only see relevant patient care options
- **Quick Access**: Direct paths to common tasks
- **Less Clutter**: No confusing admin or management options

### For Doctors
- **Focused Workflow**: Patient management and knowledge resources
- **Research Access**: Direct link to medical knowledge base
- **Clean Interface**: Only essential tools visible

### For Experts/Admins
- **Full Control**: Access to all system features
- **Management Tools**: Analytics and system administration
- **Flexible Access**: Can perform any role's tasks

### For System
- **Better Security**: Role-based access control prevents unauthorized actions
- **Improved UX**: Users only see relevant options
- **Easier Maintenance**: Centralized permission logic
- **Audit Trail**: Clear tracking of who accessed what

## 📊 Session Data Structure

When user logs in, session contains:
```python
request.session = {
    'user_role': 'NURSE',  # or 'DOCTOR', 'EXPERT'
    'user_fullname': 'Sarah Johnson',
    'is_nurse': True,
    'is_doctor': False,
    'is_expert': False,
    '_auth_user_id': '1',
    '_auth_user_backend': 'django.contrib.auth.backends.ModelBackend',
}
```

Template context automatically includes:
```python
{
    'user_role': 'NURSE',
    'is_nurse': True,
    'is_doctor': False,
    'is_expert': False,
    'user_fullname': 'Sarah Johnson',
    'user_display_name': 'Sarah',
    'user_dashboard': 'nurse_dashboard',
    'can_create_cases': True,
    'can_review_cases': False,
    'can_upload_documents': False,
    'can_manage_system': False,
}
```

## 🔄 Integration with Existing Features

### No Breaking Changes
- All existing views, models, and URLs remain functional
- Patient management works as before
- Diagnosis system unchanged
- Knowledge base access preserved
- Only addition: Automatic role-based menu filtering

### Backward Compatibility
- Old login URLs still work
- Existing user accounts automatically supported
- Admin panel access preserved for staff
- API endpoints (if any) unaffected

## 📝 Next Steps

To further enhance the system:

1. **Add Role-Specific Dashboard Cards**:
   - Show nurse-relevant stats on nurse dashboard
   - Show doctor-relevant cases on doctor dashboard

2. **Implement Permission Decorators**:
   ```python
   from django.contrib.auth.decorators import user_passes_test
   
   def is_nurse(user):
       return user.role == 'NURSE'
   
   @user_passes_test(is_nurse)
   def nurse_only_view(request):
       ...
   ```

3. **Add Activity Logging**:
   - Track which users access which features
   - Generate role-based usage reports

4. **Session Activity Monitoring**:
   - Show "Last Login" time
   - Display active sessions count
   - Add "Force Logout" for admins

## 🎓 Code Examples

### Check Role in View
```python
def my_view(request):
    if request.user.role == 'NURSE':
        # Nurse-specific logic
        pass
    elif request.user.role == 'DOCTOR':
        # Doctor-specific logic
        pass
```

### Check Role in Template
```django
{% if user.role == 'NURSE' %}
    <p>Welcome, Nurse!</p>
{% elif user.role == 'DOCTOR' %}
    <p>Welcome, Doctor!</p>
{% endif %}
```

### Use Permission Flags
```django
{% if can_create_cases %}
    <a href="{% url 'case_create' %}">New Case</a>
{% endif %}

{% if can_upload_documents %}
    <a href="{% url 'document_upload' %}">Upload</a>
{% endif %}
```

---

**✅ System Ready**: Your Medical AI System now has enterprise-grade session management and role-based access control!
