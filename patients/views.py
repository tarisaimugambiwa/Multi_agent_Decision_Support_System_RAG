from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.utils import OperationalError

from .models import Patient, MedicalRecord
from .forms import PatientForm
from diagnoses.models import Case, Notification
from users.models import User


class PatientListView(LoginRequiredMixin, ListView):
    """
    Class-based ListView for displaying all patients with search and filtering.
    """
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """
        Filter patients based on search query and other filters.
        """
        queryset = super().get_queryset()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        
        # Gender filter
        gender = self.request.GET.get('gender', '')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Age range filter
        age_min = self.request.GET.get('age_min', '')
        age_max = self.request.GET.get('age_max', '')
        
        if age_min or age_max:
            today = timezone.now().date()
            if age_min:
                min_birth_date = today - timedelta(days=int(age_min) * 365)
                queryset = queryset.filter(date_of_birth__lte=min_birth_date)
            if age_max:
                max_birth_date = today - timedelta(days=int(age_max) * 365)
                queryset = queryset.filter(date_of_birth__gte=max_birth_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        context['age_min'] = self.request.GET.get('age_min', '')
        context['age_max'] = self.request.GET.get('age_max', '')
        context['total_patients'] = Patient.objects.count()
        
        # Gender choices for filter dropdown
        context['gender_choices'] = Patient.GENDER_CHOICES
        
        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    """
    Class-based CreateView for adding new patients.
    """
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patients:patient_list')
    
    def form_valid(self, form):
        """
        Add success message when patient is created successfully.
        """
        messages.success(
            self.request, 
            f'Patient {form.instance.full_name} has been created successfully!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Add error message when form is invalid.
        """
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


class PatientDetailView(LoginRequiredMixin, DetailView):
    """
    Class-based DetailView for displaying patient details and medical records.
    """
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        print(f"Looking for patient with ID: {pk}")  # Debug log
        patient = get_object_or_404(Patient, pk=pk)
        print(f"Found patient: {patient.first_name} {patient.last_name}")  # Debug log
        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the correct related_name 'medical_records' instead of 'medicalrecord_set'
        context['medical_records'] = self.object.medical_records.all().order_by('-visit_date')
        # Add patient's cases
        context['cases'] = self.object.cases.all().order_by('-created_at')
        # Add patient age
        context['patient_age'] = self.object.get_age()
        return context


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Class-based UpdateView for editing patient information.
    """
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    
    def get_success_url(self):
        """
        Redirect to patient detail page after successful update.
        """
        return reverse_lazy('patients:patient_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """
        Add success message when patient is updated successfully.
        """
        messages.success(
            self.request,
            f'Patient {form.instance.full_name} has been updated successfully!'
        )
        return super().form_valid(form)


class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Class-based DeleteView for removing patients (admin/expert only).
    """
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patients:patient_list')
    
    def test_func(self):
        """
        Only allow admin users and experts to delete patients.
        """
        return self.request.user.is_staff or self.request.user.role == 'EXPERT'
    
    def delete(self, request, *args, **kwargs):
        """
        Add success message when patient is deleted.
        """
        patient = self.get_object()
        messages.success(
            request,
            f'Patient {patient.full_name} has been deleted successfully.'
        )
        return super().delete(request, *args, **kwargs)


@login_required
def nurse_dashboard(request):
    """
    Nurse dashboard view showing recent cases and statistics.
    """
    # Only allow nurses to access this dashboard
    if request.user.role != 'NURSE':
        messages.error(request, 'Access denied. This dashboard is for nurses only.')
        return render(request, 'error.html', {'error_code': '403'})
    
    # Get current nurse's cases
    nurse_cases = Case.objects.filter(nurse=request.user).order_by('-created_at')
    
    # Statistics for the nurse
    my_cases_count = nurse_cases.filter(
        status__in=['PENDING', 'IN_PROGRESS', 'DOCTOR_REVIEW']
    ).count()
    
    # Count cases that have been reviewed by a doctor
    doctor_reviewed_count = nurse_cases.filter(
        doctor_review__isnull=False,
        reviewed_by__isnull=False
    ).count()
    
    urgent_cases_count = Case.objects.filter(
        priority__in=['URGENT', 'CRITICAL'],
        status__in=['PENDING', 'IN_PROGRESS']
    ).count()
    
    pending_cases_count = nurse_cases.filter(status='PENDING').count()
    
    # Cases completed today
    today = timezone.now().date()
    completed_today = nurse_cases.filter(
        status='COMPLETED',
        updated_at__date=today
    ).count()
    
    # Recent cases (last 20 for the nurse)
    recent_cases = nurse_cases[:20]
    
    # Paginate recent cases
    paginator = Paginator(recent_cases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Notifications for the nurse (unread count + recent items)
    try:
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user,
            read_at__isnull=True
        ).count()

        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:6]
    except OperationalError as e:
        # Database table probably doesn't exist yet (migrations pending).
        # Fall back to safe defaults so the dashboard still loads.
        print(f"Notification table missing or DB error: {e}")
        unread_notifications_count = 0
        recent_notifications = []

    context = {
        'recent_cases': page_obj,
        'my_cases_count': my_cases_count,
        'doctor_reviewed_count': doctor_reviewed_count,
        'urgent_cases_count': urgent_cases_count,
        'pending_cases_count': pending_cases_count,
        'completed_today': completed_today,
        'total_patients': Patient.objects.count(),
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'nurse_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    """
    Doctor dashboard view showing cases requiring review and AI analysis.
    """
    import json
    
    # Only allow doctors to access this dashboard
    if request.user.role != 'DOCTOR':
        messages.error(request, 'Access denied. This dashboard is for doctors only.')
        return render(request, 'error.html', {'error_code': '403'})
    
    # Get cases requiring doctor review
    pending_cases = Case.objects.filter(
        status__in=['DOCTOR_REVIEW', 'IN_PROGRESS']
    ).select_related('patient', 'nurse').order_by('-created_at')
    
    # Parse AI diagnosis for each case
    for case in pending_cases:
        if case.ai_diagnosis:
            try:
                case.ai_diagnosis_parsed = json.loads(case.ai_diagnosis)
            except json.JSONDecodeError:
                case.ai_diagnosis_parsed = {}
        else:
            case.ai_diagnosis_parsed = {}
    
    # Statistics for doctor dashboard
    pending_reviews_count = Case.objects.filter(status='DOCTOR_REVIEW').count()
    
    critical_cases_count = Case.objects.filter(
        priority__in=['CRITICAL', 'URGENT'],
        status__in=['PENDING', 'IN_PROGRESS', 'DOCTOR_REVIEW']
    ).count()
    
    # AI assisted cases today
    today = timezone.now().date()
    ai_assisted_today = Case.objects.filter(
        created_at__date=today
    ).exclude(ai_diagnosis__exact='').count()
    
    # Cases reviewed today by this doctor
    reviewed_today = Case.objects.filter(
        doctor=request.user,
        updated_at__date=today,
        status='COMPLETED'
    ).count()
    
    # Calculate AI performance metrics
    completed_cases_with_ai = Case.objects.filter(
        status='COMPLETED',
        created_at__date__gte=today - timedelta(days=7)
    ).exclude(ai_diagnosis__exact='')
    
    ai_accuracy_rate = 85  # Default placeholder
    avg_ai_confidence = 0
    
    if completed_cases_with_ai.exists():
        confidence_sum = 0
        confidence_count = 0
        
        for case in completed_cases_with_ai:
            try:
                ai_data = json.loads(case.ai_diagnosis)
                confidence = ai_data.get('diagnostic_confidence', 0)
                if confidence:
                    confidence_sum += float(confidence)
                    confidence_count += 1
            except (json.JSONDecodeError, ValueError):
                continue
        
        if confidence_count > 0:
            avg_ai_confidence = int(confidence_sum / confidence_count * 100)
    
    # Recent activities (placeholder data)
    recent_activities = [
        {
            'timestamp': timezone.now() - timedelta(minutes=15),
            'description': 'Reviewed case #123 - Approved AI diagnosis',
            'icon': 'check-circle',
            'color': 'success'
        },
        {
            'timestamp': timezone.now() - timedelta(hours=1),
            'description': 'Case #124 marked as critical priority',
            'icon': 'exclamation-triangle',
            'color': 'warning'
        },
        {
            'timestamp': timezone.now() - timedelta(hours=2),
            'description': 'Completed review of 3 cases',
            'icon': 'clipboard-check',
            'color': 'info'
        },
    ]
    
    context = {
        'pending_cases': pending_cases[:50],  # Limit to 50 for performance
        'pending_reviews_count': pending_reviews_count,
        'critical_cases_count': critical_cases_count,
        'ai_assisted_today': ai_assisted_today,
        'reviewed_today': reviewed_today,
        'ai_accuracy_rate': ai_accuracy_rate,
        'avg_ai_confidence': avg_ai_confidence,
        'recent_activities': recent_activities,
        'total_cases': Case.objects.count(),
    }
    # Notifications for doctor (unread count + recent items)
    try:
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user,
            read_at__isnull=True
        ).count()

        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:6]
    except Exception:
        # If notifications table missing, fall back to defaults
        unread_notifications_count = 0
        recent_notifications = []

    context.update({
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
    })
    
    return render(request, 'doctor_dashboard.html', context)


class MedicalRecordListView(LoginRequiredMixin, ListView):
    """
    Class-based ListView for displaying medical records.
    """
    model = MedicalRecord
    template_name = 'patients/medical_record_list.html'
    context_object_name = 'medical_records'
    paginate_by = 15
    ordering = ['-visit_date']
    
    def get_queryset(self):
        """
        Filter medical records based on search and patient.
        """
        queryset = super().get_queryset()
        
        # Filter by patient if specified
        patient_id = self.request.GET.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(symptoms__icontains=search_query) |
                Q(diagnosis__icontains=search_query) |
                Q(treatment__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['patient_filter'] = self.request.GET.get('patient', '')
        context['patients'] = Patient.objects.all().order_by('last_name', 'first_name')
        return context


class MedicalRecordCreateView(LoginRequiredMixin, CreateView):
    """
    Class-based CreateView for adding new medical records.
    """
    model = MedicalRecord
    template_name = 'patients/medical_record_form.html'
    fields = ['patient', 'visit_date', 'symptoms', 'diagnosis', 'treatment', 'notes']
    success_url = reverse_lazy('patients:medical_record_list')
    
    def form_valid(self, form):
        """
        Set the user to current user and add success message.
        """
        form.instance.user = self.request.user
        messages.success(
            self.request,
            f'Medical record for {form.instance.patient.full_name} has been created successfully!'
        )
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        """
        Customize the form to set initial values and widget attributes.
        """
        form = super().get_form(form_class)
        
        # Set initial visit date to current time
        form.fields['visit_date'].initial = timezone.now()
        
        # Add CSS classes to form fields
        for field_name, field in form.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Special handling for textarea fields
        if 'symptoms' in form.fields:
            form.fields['symptoms'].widget.attrs.update({
                'rows': 4,
                'placeholder': 'Describe the patient\'s symptoms...'
            })
        
        if 'diagnosis' in form.fields:
            form.fields['diagnosis'].widget.attrs.update({
                'rows': 3,
                'placeholder': 'Enter diagnosis...'
            })
        
        if 'treatment' in form.fields:
            form.fields['treatment'].widget.attrs.update({
                'rows': 3,
                'placeholder': 'Describe treatment plan...'
            })
        
        if 'notes' in form.fields:
            form.fields['notes'].widget.attrs.update({
                'rows': 3,
                'placeholder': 'Additional notes...'
            })
        
        return form


class MedicalRecordDetailView(LoginRequiredMixin, DetailView):
    """
    Class-based DetailView for displaying medical record details.
    """
    model = MedicalRecord
    template_name = 'patients/medical_record_detail.html'
    context_object_name = 'medical_record'


def patient_search_api(request):
    """
    AJAX API endpoint for patient search with filters
    """
    query = request.GET.get('q', '').strip()
    print(f"Search query: {query}")  # Debug log
    
    if len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Please enter at least 2 characters'
        })

    # Get patients matching the query
    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone_number__icontains=query) |
        Q(address__icontains=query)
    ).order_by('last_name', 'first_name')[:10]

    # Debug logging
    print(f"Found {patients.count()} matching patients")

    results = []
    for patient in patients:
        print(f"Processing patient: ID={patient.id}, Name={patient.first_name} {patient.last_name}")
        if patient.id:  # Ensure we have a valid ID
            results.append({
                'id': patient.id,
                'patient_id': f"P{str(patient.id).zfill(4)}",  # Generate patient ID from database ID
                'name': f"{patient.first_name} {patient.last_name}",
                'phone': patient.phone_number or '-'
            })

    return JsonResponse({
        'results': results,
        'message': '' if results else f'No patients found matching "{query}"'
    })


def dashboard_stats_api(request):
    """
    AJAX API endpoint for dashboard statistics.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Basic statistics
    stats = {
        'total_patients': Patient.objects.count(),
        'total_records': MedicalRecord.objects.count(),
        'total_cases': Case.objects.count(),
    }
    
    # Role-specific statistics
    if request.user.role == 'NURSE':
        stats.update({
            'my_cases': Case.objects.filter(nurse=request.user).count(),
            'my_pending_cases': Case.objects.filter(
                nurse=request.user, 
                status='PENDING'
            ).count(),
        })
    elif request.user.role == 'DOCTOR':
        stats.update({
            'my_cases': Case.objects.filter(doctor=request.user).count(),
            'pending_reviews': Case.objects.filter(
                status='DOCTOR_REVIEW'
            ).count(),
        })
    
    # Recent activity
    today = timezone.now().date()
    stats.update({
        'patients_today': Patient.objects.filter(created_at__date=today).count(),
        'records_today': MedicalRecord.objects.filter(created_at__date=today).count(),
        'cases_today': Case.objects.filter(created_at__date=today).count(),
    })
    
    return JsonResponse(stats)


def recent_patients_api(request):
    """
    AJAX API endpoint for recent patients
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Get patients with recent activity (cases or medical records)
        recent_limit = timezone.now() - timedelta(days=30)
        
        patients_qs = Patient.objects.filter(
            Q(cases__created_at__gte=recent_limit) |
            Q(medical_records__created_at__gte=recent_limit)
        ).distinct().order_by('-created_at')[:10]
        
        patients_data = []
        for patient in patients_qs:
            patients_data.append({
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'last_activity': patient.cases.first().created_at.isoformat() if patient.cases.first() else None
            })
        
        return JsonResponse({
            'patients': patients_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def patient_detail_api(request, patient_id):
    """
    AJAX API endpoint for patient details
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Calculate age
        age = None
        if patient.date_of_birth:
            today = timezone.now().date()
            age = today.year - patient.date_of_birth.year
            if today.month < patient.date_of_birth.month or \
               (today.month == patient.date_of_birth.month and today.day < patient.date_of_birth.day):
                age -= 1
        
        # Get recent cases count
        recent_cases_count = patient.cases.count()
        
        patient_data = {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'phone_number': patient.phone_number,
            'email': patient.email,
            'gender': patient.get_gender_display(),
            'age': age,
            'recent_cases_count': recent_cases_count,
            'allergies': patient.allergies,
            'emergency_contact': patient.emergency_contact,
            'insurance_info': patient.insurance_info
        }
        
        return JsonResponse(patient_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def patient_search_view(request):
    """
    Main patient search page view
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'total_patients': Patient.objects.count(),
        'title': 'Patient Search'
    }
    
    return render(request, 'patient_search.html', context)
