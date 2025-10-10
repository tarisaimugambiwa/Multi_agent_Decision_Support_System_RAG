# Knowledge Base Access Control

## Overview
The Medical Knowledge Base system is **restricted to Doctors only**. This ensures that medical research, guidelines, and protocols are reviewed and managed by qualified medical professionals.

## Access Rules

### ✅ Who Can Access:
- **Doctors** (users with `role='DOCTOR'`)
- **Admin/Staff** (users with `is_staff=True` or `is_superuser=True`)

### ❌ Who Cannot Access:
- **Nurses** (users with `role='NURSE'`)
- **Other user roles**

## Implementation

### 1. View Protection
All knowledge base views include access control:
```python
def check_doctor_access(user):
    """Check if user is a doctor or admin"""
    return user.role == 'DOCTOR' or user.is_staff or user.is_superuser
```

Protected views:
- `/knowledge/` - Knowledge Base Dashboard
- `/knowledge/documents/` - Document Library
- `/knowledge/documents/<id>/` - Document Detail
- `/knowledge/upload/` - Document Upload
- `/knowledge/search/` - AI Search

### 2. UI Access
- **Doctor Dashboard**: Knowledge Base button visible in header (white button next to "New Case")
- **Nurse Dashboard**: No Knowledge Base button (removed for clarity)

### 3. Access Denied Behavior
If a nurse or unauthorized user tries to access the Knowledge Base:
- Redirected to home page
- Error message: "Access denied. Knowledge Base is only available to doctors."

## URL Structure

```
/knowledge/                     # Dashboard (Doctor only)
/knowledge/documents/           # Document list (Doctor only)
/knowledge/documents/<id>/      # Document detail (Doctor only)
/knowledge/upload/              # Upload form (Doctor only)
/knowledge/search/              # AI search (Doctor only)
```

## Testing Access

### Test as Doctor:
1. Login with doctor credentials (username: `doctor`, password: `doctor123` or admin credentials)
2. Access Doctor Dashboard at `/doctor-dashboard/`
3. Click "Knowledge Base" button in header
4. You should see the Knowledge Base dashboard

### Test as Nurse:
1. Login with nurse credentials (username: `tarisaim` or `User`)
2. Access Nurse Dashboard at `/nurse-dashboard/`
3. No Knowledge Base button should be visible
4. If you manually navigate to `/knowledge/`, you'll be redirected with an error message

## Rationale

This access restriction ensures:
1. **Medical Authority**: Only qualified doctors manage medical knowledge
2. **Workflow Clarity**: Nurses focus on patient care and case creation
3. **Data Integrity**: Medical documents and guidelines are curated by professionals
4. **Role Separation**: Clear separation of responsibilities between nurses and doctors

## Future Enhancements

Consider adding:
- Read-only access for nurses (view but not upload)
- Document approval workflow (nurse uploads, doctor approves)
- Activity logging for knowledge base access
- Custom permissions per document type
