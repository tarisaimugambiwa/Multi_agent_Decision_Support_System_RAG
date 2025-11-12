# Doctor's Comments on AI Diagnosis Feature

## Overview
Added a new section allowing doctors to comment on and assess the AI-powered diagnosis, separate from the treatment plan comments.

## Changes Made

### 1. Database Model (`diagnoses/models.py`)
Added two new fields to the `Case` model:
- `diagnosis_comments` (TextField, blank=True) - Stores doctor's assessment of AI diagnosis
- `diagnosis_comments_date` (DateTimeField, null=True, blank=True) - Timestamp when comments were added

### 2. Database Migration
Created and applied migration:
- **Migration File**: `diagnoses/migrations/0008_case_diagnosis_comments_case_diagnosis_comments_date.py`
- **Status**: ✅ Applied successfully
- **Command**: `python manage.py migrate diagnoses`

### 3. Backend View (`diagnoses/views.py`)
Added new AJAX endpoint function:
```python
@login_required
@require_http_methods(["POST"])
def save_diagnosis_comments(request, case_id):
    """Save doctor's comments on AI diagnosis (AJAX)."""
    # Validates doctor role
    # Saves comments and timestamp
    # Returns JSON response
```

**Features**:
- Role-based access control (only doctors can save)
- Validates non-empty comments
- Timestamps comments automatically
- Returns JSON success/error response

### 4. URL Configuration (`diagnoses/urls.py`)
Added new API endpoint:
```python
path('api/diagnosis-comments/<int:case_id>/', views.save_diagnosis_comments, name='save_diagnosis_comments'),
```

### 5. Frontend Template (`templates/diagnoses/case_detail.html`)

#### New Section: Doctor's Assessment of AI Diagnosis
**Location**: Immediately after AI-Powered Diagnosis section, before Treatment Plan

**Doctor View**:
- Cyan/teal themed section (distinct from yellow treatment comments)
- Shows input form if no comments exist (with helpful guidance)
- Shows existing comments with timestamp and edit button
- Edit button toggles between display and edit modes
- Save/Cancel buttons for form actions

**Nurse View**:
- Only visible AFTER doctor has written diagnosis comments
- Shows doctor's assessment in read-only mode
- Displays timestamp of when assessment was provided

**Styling**:
- Background: Gradient from light cyan to light purple
- Border: Left 5px solid cyan (#00bcd4)
- Header: Teal color with stethoscope icon
- Alert boxes: Blue/green gradient background

### 6. JavaScript Functions (case_detail.html)

#### `saveDiagnosisComments()`
- Validates textarea content
- Sends POST request to `/diagnoses/api/diagnosis-comments/` endpoint
- Shows loading state on button
- Reloads page on success
- Handles errors gracefully

#### `showEditDiagnosisComments()`
- Hides comment display section
- Shows edit form
- Shows cancel button
- Focuses on textarea

#### `cancelDiagnosisComments()`
- Hides edit form
- Shows comment display section
- Restores original view

#### Auto-initialization on page load
- Sets initial visibility based on whether comments exist
- Form hidden if comments exist, shown if empty

## Workflow

### Doctor Workflow
1. Doctor opens case detail page
2. Scrolls to "Doctor's Assessment of AI Diagnosis" section (cyan-themed)
3. **If no comments exist**:
   - Sees guidance text and empty textarea
   - Enters assessment of AI diagnosis accuracy and recommendations
   - Clicks "Save Assessment" button
   - Page reloads and shows saved comments

4. **If comments exist**:
   - Sees existing assessment with timestamp
   - Can click "Edit" button to modify
   - Changes text and clicks "Save Assessment"
   - Page reloads with updated comments

### Nurse Workflow
1. Nurse creates case with symptoms and vital signs
2. Cannot see diagnosis comments section yet
3. **After doctor writes diagnosis comments**:
   - Nurse opens case detail page
   - Sees "Doctor's Assessment of AI Diagnosis" section in read-only mode
   - Cannot modify, only view
   - Helps nurse understand doctor's evaluation of AI results

## Technical Details

### CSRF Protection
- Uses Django's CSRF middleware
- Token retrieved from form element
- Passed in fetch headers

### Error Handling
- Empty comment validation
- Role verification (doctor only)
- JSON parsing error handling
- Generic exception catching
- User-friendly error messages

### Data Flow
1. User submits form → JavaScript validates
2. AJAX POST to `/diagnoses/api/diagnosis-comments/{case_id}/`
3. Django view checks permission and saves to database
4. Returns JSON success response
5. JavaScript reloads page to show new comments

## Key Distinctions

### Treatment Comments vs Diagnosis Comments

| Aspect | Treatment Comments | Diagnosis Comments |
|--------|-------------------|-------------------|
| **Section Color** | Yellow/Gold | Cyan/Teal |
| **Icon** | Prescription pad | Stethoscope |
| **About** | Doctor's review of treatment plan | Doctor's assessment of AI diagnosis |
| **Database Fields** | `treatment_comments` | `diagnosis_comments` |
| **Endpoint** | `/api/treatment-comments/` | `/api/diagnosis-comments/` |
| **Form ID** | `treatmentCommentsText` | `diagnosis-comments-textarea` |

## Testing Checklist

- [ ] Doctor can add diagnosis comments
- [ ] Comments save with correct timestamp
- [ ] Doctor can edit existing comments
- [ ] Nurse cannot see section until comments exist
- [ ] Nurse can view comments in read-only mode after they're added
- [ ] CSRF protection works (token validation)
- [ ] Error messages display on validation failures
- [ ] Loading state shows during save

## Files Modified
1. `diagnoses/models.py` - Added model fields
2. `diagnoses/views.py` - Added save_diagnosis_comments view
3. `diagnoses/urls.py` - Added API endpoint
4. `diagnoses/migrations/0008_*.py` - Database schema update
5. `templates/diagnoses/case_detail.html` - Added UI and JavaScript

## Database Status
✅ Migration applied: `diagnoses.0008_case_diagnosis_comments_case_diagnosis_comments_date`

## Notes
- Section only visible to doctors initially
- Nurses see after doctor writes comments
- Edit functionality available for doctors
- Timestamps show in "M d, Y - H:i" format (e.g., "Nov 10, 2025 - 15:30")
- No validation on comment length (allows any text)
- Comments cleared when page reloaded (data-bind to database on each save)
