import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.forms import ModelForm
from django import forms
from django.db import models
from django.db.models import Q

from .models import Case
from .ai_utils import get_ai_diagnosis, analyze_case_urgency
from patients.models import Patient, MedicalRecord

# Import Multi-Agent System
from .services import (
    CoordinatorAgent,
    RetrieverAgent,
    DiagnosisAgent,
    TreatmentAgent
)


class CaseForm(ModelForm):
    """Form for creating and editing diagnostic cases."""
    
    # Override vital_signs to make it explicitly not required
    vital_signs = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = Case
        fields = ['patient', 'symptoms', 'vital_signs', 'priority']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe patient symptoms, chief complaints, and relevant observations...',
                'class': 'form-control'
            }),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_vital_signs(self):
        """Validate and clean vital signs JSON data."""
        vital_signs = self.cleaned_data.get('vital_signs', '{}')
        
        # Handle None or empty values
        if vital_signs is None or (isinstance(vital_signs, str) and not vital_signs.strip()):
            return {}
        
        try:
            # Try to parse as JSON
            if isinstance(vital_signs, str):
                parsed_data = json.loads(vital_signs)
            else:
                parsed_data = vital_signs
            
            # Validate that it's a dictionary
            if not isinstance(parsed_data, dict):
                raise forms.ValidationError("Vital signs must be in JSON format")
            
            return parsed_data
            
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for vital signs")


class CaseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create view for diagnostic cases with AI diagnosis integration.
    Only accessible to nurses and doctors.
    """
    model = Case
    form_class = CaseForm
    template_name = 'diagnoses/case_form.html'
    success_url = reverse_lazy('diagnoses:case_list')
    
    def test_func(self):
        """Only nurses and doctors can create cases."""
        return self.request.user.role in ['NURSE', 'DOCTOR']
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Diagnostic Case'
        context['patients'] = Patient.objects.all().order_by('last_name', 'first_name')
        
        # Handle pre-selected patient from search
        selected_patient_id = self.request.GET.get('patient')
        if selected_patient_id:
            try:
                selected_patient = Patient.objects.get(id=selected_patient_id)
                context['selected_patient'] = selected_patient
                context['title'] = f'New Diagnosis for {selected_patient.full_name}'
            except Patient.DoesNotExist:
                pass
        
        return context
    
    def get_initial(self):
        """Set initial form values, including pre-selected patient."""
        initial = super().get_initial()
        
        # Pre-select patient if provided in URL
        selected_patient_id = self.request.GET.get('patient')
        if selected_patient_id:
            try:
                Patient.objects.get(id=selected_patient_id)
                initial['patient'] = selected_patient_id
            except Patient.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        """
        Process form and generate AI diagnosis using Multi-Agent System.
        """
        try:
            # Set the nurse (current user)
            form.instance.nurse = self.request.user
            
            # Get patient and symptoms from form
            patient = form.cleaned_data['patient']
            symptoms = form.cleaned_data['symptoms']
            vital_signs = form.cleaned_data.get('vital_signs', {})
            
            # Save the case first (to get an ID)
            self.object = form.save(commit=False)
            self.object.save()
            
            # ===== MULTI-AGENT SYSTEM WORKFLOW =====
            
            # 1. Initialize all agents
            coordinator = CoordinatorAgent()
            retriever = RetrieverAgent()
            diagnosis_agent = DiagnosisAgent()
            treatment_agent = TreatmentAgent()
            
            # 2. COORDINATOR: Route the case and assess urgency
            routing_decision = coordinator.route_case(self.object, symptoms, vital_signs)
            
            # 3. RETRIEVER: Search medical knowledge base with symptoms
            # Convert symptoms to list format
            symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
            retriever_results = retriever.search_protocols(
                query=symptoms, 
                symptoms=symptom_list,
                top_k=5
            )
            
            # Get cardiac emergency protocol if needed
            if 'cardiac' in symptoms.lower() or 'chest pain' in symptoms.lower():
                cardiac_protocol = retriever.retrieve_cardiac_emergency_protocol()
                retriever_results['cardiac_protocol'] = cardiac_protocol
            
            # 4. DIAGNOSIS: Analyze symptoms and generate diagnoses
            patient_history = {
                'medical_history': patient.medical_history,
                'allergies': patient.allergies,
            }
            
            demographics = {
                'age': getattr(patient, 'age', 'unknown'),
                'gender': patient.get_gender_display(),
            }
            
            diagnosis_results = diagnosis_agent.analyze_symptoms(
                symptoms=symptoms,
                patient_history=patient_history,
                demographics=demographics,
                vital_signs=vital_signs,
                retriever_context=retriever_results
            )
            
            # 5. TREATMENT: Create action plan and recommendations
            # Always generate treatment recommendations for all urgency levels
            treatment_results = treatment_agent.create_action_plan(
                diagnosis=diagnosis_results,
                urgency_level=routing_decision['urgency_level'],
                symptoms=symptom_list,
                red_flags=diagnosis_results.get('red_flags', []),
                emergency_conditions=diagnosis_results.get('emergency_conditions', [])
            )
            
            # Get medication recommendations with symptoms
            medication_plan = treatment_agent.recommend_medications(
                diagnosis=diagnosis_results,
                symptoms=symptom_list,
                patient_history=patient_history,
                allergies=[patient.allergies] if patient.allergies else []
            )
            treatment_results['medications'] = medication_plan
            
            # Get first aid instructions if critical
            if routing_decision['urgency_level'] == 'critical':
                first_aid = treatment_agent.provide_first_aid(
                    diagnosis_results['primary_diagnosis']
                )
                treatment_results['first_aid'] = first_aid
            
            # 6. COORDINATOR: Coordinate all agent results
            coordinated_result = coordinator.coordinate_agents(
                self.object,
                retriever_results,
                diagnosis_results,
                treatment_results
            )
            
            # ===== UPDATE CASE WITH AGENT RESULTS =====
            
            # Compile comprehensive AI diagnosis
            # Ensure confidence is a percentage (0-100)
            confidence_percentage = diagnosis_results['confidence_score']
            if confidence_percentage <= 1.0:
                confidence_percentage = confidence_percentage * 100
            
            comprehensive_diagnosis = {
                'multi_agent_system': 'HealthFlow DMS v1.0',
                'timestamp': timezone.now().isoformat(),
                'routing': routing_decision,
                'retriever': {
                    'knowledge_base_results': retriever_results.get('results', []),
                    'sources': retriever_results.get('sources', []),
                    'total_documents': retriever_results.get('total_found', 0)
                },
                'diagnosis': {
                    'primary_diagnosis': diagnosis_results['primary_diagnosis'],
                    'confidence': round(confidence_percentage, 1),  # Ensure percentage format
                    'explanation': diagnosis_results.get('explanation', ''),  # Plain language explanation
                    'differential_diagnoses': diagnosis_results['differential_diagnoses'],
                    'red_flags': diagnosis_results['red_flags'],
                    'emergency_conditions': diagnosis_results['emergency_conditions'],
                    'recommended_tests': diagnosis_results['recommended_tests'],
                },
                'treatment': treatment_results,
                'coordination': coordinated_result,
            }
            
            # Save to case
            self.object.ai_diagnosis = json.dumps(comprehensive_diagnosis, indent=2)
            self.object.priority = routing_decision['priority']
            self.object.status = routing_decision['recommended_status']
            self.object.save()
            
            # ===== USER FEEDBACK =====
            
            # Display appropriate message based on urgency
            if routing_decision['urgency_level'] == 'critical':
                messages.error(
                    self.request,
                    f"🚨 CRITICAL CASE! {routing_decision['routing_reason']} - "
                    f"Emergency Conditions: {', '.join(diagnosis_results.get('emergency_conditions', ['Unknown']))}"
                )
            elif routing_decision['urgency_level'] == 'high':
                messages.warning(
                    self.request,
                    f"⚠️ HIGH PRIORITY: {diagnosis_results['primary_diagnosis']} - "
                    f"Doctor review recommended."
                )
            else:
                messages.success(
                    self.request,
                    f"✅ Case created successfully! AI Diagnosis: {diagnosis_results['primary_diagnosis']} "
                    f"(Confidence: {diagnosis_results['confidence_score']:.1%})"
                )
            
            # Additional red flag warnings
            if diagnosis_results.get('red_flags'):
                for flag in diagnosis_results['red_flags'][:3]:  # Show top 3
                    messages.warning(
                        self.request,
                        f"⚠️ Red Flag Detected: {flag['flag'].upper()} - {flag['action']}"
                    )
            
            # Redirect to AI Report instead of case list
            messages.info(
                self.request,
                "📊 View the complete AI-generated medical report below."
            )
            return redirect('diagnoses:case_detail', pk=self.object.pk)
            
        except Exception as e:
            # Handle errors gracefully
            messages.error(
                self.request,
                f"Case created but multi-agent analysis failed: {str(e)}. "
                "Please review manually."
            )
            
            # Save basic case info
            if not self.object.ai_diagnosis:
                self.object.ai_diagnosis = json.dumps({
                    'error': str(e),
                'timestamp': timezone.now().isoformat(),
                'manual_review_required': True
            })
            return super().form_valid(form)
    
    def _prepare_patient_history(self, patient, vital_signs):
        """
        Prepare comprehensive patient history for AI diagnosis.
        
        Args:
            patient: Patient model instance
            vital_signs: Dictionary of current vital signs
            
        Returns:
            Dict: Formatted patient history for AI analysis
        """
        # Get recent medical records
        recent_records = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-date')[:5]
        
        # Compile medical history
        medical_history_items = []
        medications = []
        
        for record in recent_records:
            if record.diagnosis:
                medical_history_items.append(record.diagnosis)
            if record.medications:
                medications.extend(record.medications.split(','))
        
        # Calculate age
        age = None
        if patient.date_of_birth:
            today = timezone.now().date()
            age = today.year - patient.date_of_birth.year
            if today.month < patient.date_of_birth.month or \
               (today.month == patient.date_of_birth.month and today.day < patient.date_of_birth.day):
                age -= 1
        
        return {
            'patient_id': patient.id,
            'age': age,
            'gender': patient.gender,
            'medical_history': '; '.join(set(medical_history_items)) if medical_history_items else 'None reported',
            'medications': '; '.join(set(med.strip() for med in medications)) if medications else 'None reported',
            'allergies': patient.allergies or 'None reported',
            'emergency_contact': patient.emergency_contact,
            'vital_signs': vital_signs,
            'insurance_info': patient.insurance_info or {},
        }
    
    def _map_urgency_to_priority(self, urgency_level):
        """
        Map AI urgency level to Case priority choices.
        
        Args:
            urgency_level (str): AI-determined urgency level
            
        Returns:
            str: Case priority level
        """
        urgency_mapping = {
            'critical': 'CRITICAL',
            'high': 'URGENT',
            'moderate': 'HIGH',
            'low': 'MEDIUM'
        }
        return urgency_mapping.get(urgency_level.lower(), 'MEDIUM')


class CaseListView(LoginRequiredMixin, ListView):
    """List view for diagnostic cases."""
    model = Case
    template_name = 'diagnoses/case_list.html'
    context_object_name = 'cases'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter cases based on user role."""
        queryset = Case.objects.select_related('patient', 'nurse', 'doctor')
        
        # Filter by user role
        if self.request.user.role == 'NURSE':
            # Nurses see their own cases plus cases needing review
            queryset = queryset.filter(
                models.Q(nurse=self.request.user) |
                models.Q(status='PENDING')
            )
        elif self.request.user.role == 'DOCTOR':
            # Doctors see cases assigned to them or needing doctor review
            queryset = queryset.filter(
                models.Q(doctor=self.request.user) |
                models.Q(status='DOCTOR_REVIEW') |
                models.Q(status='IN_PROGRESS')
            )
        
        # Apply filters from query parameters
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset.order_by('-created_at')


class CaseDetailView(LoginRequiredMixin, DetailView):
    """Detail view for individual diagnostic cases."""
    model = Case
    template_name = 'diagnoses/case_detail.html'
    context_object_name = 'case'
    
    def get_context_data(self, **kwargs):
        """Add AI diagnosis parsing to context."""
        context = super().get_context_data(**kwargs)
        
        # Parse AI diagnosis JSON
        ai_diagnosis_data = {}
        if self.object.ai_diagnosis:
            try:
                ai_diagnosis_data = json.loads(self.object.ai_diagnosis)
            except json.JSONDecodeError:
                ai_diagnosis_data = {'error': 'Invalid AI diagnosis format'}
        
        context['ai_diagnosis_data'] = ai_diagnosis_data
        return context


# AJAX Views for dynamic functionality
def get_patient_history_ajax(request, patient_id):
    """
    AJAX endpoint to get patient medical history for case creation.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        recent_records = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-visit_date')[:3]
        
        history_data = {
            'patient_name': patient.full_name,
            'age': patient.get_age(),
            'gender': patient.get_gender_display(),
            'allergies': patient.allergies or 'None reported',
            'recent_diagnoses': [
                {
                    'date': record.visit_date.strftime('%Y-%m-%d'),
                    'diagnosis': record.diagnosis or 'No diagnosis recorded',
                    'provider': record.user.get_full_name() if record.user else 'Unknown'
                }
                for record in recent_records
            ]
        }
        
        return JsonResponse(history_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def quick_triage_ajax(request):
    """
    AJAX endpoint for quick symptom triage analysis.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    symptoms = request.POST.get('symptoms', '').strip()
    if not symptoms:
        return JsonResponse({'error': 'Symptoms required'}, status=400)
    
    try:
        urgency_level = analyze_case_urgency(symptoms)
        priority = CaseCreateView()._map_urgency_to_priority(urgency_level)
        
        return JsonResponse({
            'urgency_level': urgency_level,
            'recommended_priority': priority,
            'message': f"Recommended priority: {priority} (Urgency: {urgency_level})"
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class CaseReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for doctors to review and approve/modify/reject AI diagnoses.
    """
    model = Case
    template_name = 'case_review.html'
    context_object_name = 'case'
    success_url = reverse_lazy('doctor_dashboard')
    
    def test_func(self):
        """Ensure only doctors can access case review."""
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, 'userprofile') and
            self.request.user.userprofile.role == 'doctor'
        )
    
    def get_context_data(self, **kwargs):
        """Add additional context for the case review template."""
        context = super().get_context_data(**kwargs)
        case = self.get_object()
        
        # Parse AI diagnosis if available
        if case.ai_diagnosis:
            try:
                context['ai_diagnosis_parsed'] = json.loads(case.ai_diagnosis)
            except (json.JSONDecodeError, TypeError):
                context['ai_diagnosis_parsed'] = None
        else:
            context['ai_diagnosis_parsed'] = None
        
        # Add nurse information
        context['nurse'] = case.nurse
        
        # Add patient vital signs if they exist
        if case.vital_signs:
            try:
                if isinstance(case.vital_signs, str):
                    context['vital_signs_parsed'] = json.loads(case.vital_signs)
                else:
                    context['vital_signs_parsed'] = case.vital_signs
            except (json.JSONDecodeError, TypeError):
                context['vital_signs_parsed'] = {}
        else:
            context['vital_signs_parsed'] = {}
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle doctor review submission."""
        case = self.get_object()
        
        # Get form data
        review_decision = request.POST.get('review_decision')
        doctor_notes = request.POST.get('doctor_notes', '').strip()
        
        # Validate required fields
        if not review_decision or not doctor_notes:
            messages.error(request, 'Review decision and notes are required.')
            return self.get(request, *args, **kwargs)
        
        if len(doctor_notes) < 20:
            messages.error(request, 'Please provide more detailed notes (at least 20 characters).')
            return self.get(request, *args, **kwargs)
        
        try:
            # Update case with doctor review
            case.doctor_review = doctor_notes
            case.reviewed_by = request.user
            case.reviewed_at = timezone.now()
            
            # Handle different review decisions
            if review_decision == 'approve':
                case.status = 'completed'
                case.final_diagnosis = self._extract_ai_diagnosis_summary(case)
                case.doctor_decision = 'approved'
                
                messages.success(
                    request, 
                    'AI diagnosis approved successfully. Case marked as completed.'
                )
                
            elif review_decision == 'modify':
                modified_diagnosis = request.POST.get('modified_diagnosis', '').strip()
                case.status = 'completed'
                case.final_diagnosis = modified_diagnosis or doctor_notes
                case.doctor_decision = 'modified'
                
                # Store modification details
                case.doctor_modifications = json.dumps({
                    'original_ai_diagnosis': case.ai_diagnosis,
                    'modified_diagnosis': modified_diagnosis,
                    'modification_notes': doctor_notes,
                    'modified_at': timezone.now().isoformat()
                })
                
                messages.success(
                    request, 
                    'AI diagnosis modified successfully. Case marked as completed.'
                )
                
            elif review_decision == 'reject':
                alternative_diagnosis = request.POST.get('alternative_diagnosis', '').strip()
                rejection_reason = request.POST.get('rejection_reason', '')
                
                if not alternative_diagnosis:
                    messages.error(request, 'Alternative diagnosis is required when rejecting AI diagnosis.')
                    return self.get(request, *args, **kwargs)
                
                case.status = 'completed'
                case.final_diagnosis = alternative_diagnosis
                case.doctor_decision = 'rejected'
                
                # Store rejection details
                case.doctor_rejection = json.dumps({
                    'original_ai_diagnosis': case.ai_diagnosis,
                    'alternative_diagnosis': alternative_diagnosis,
                    'rejection_reason': rejection_reason,
                    'rejection_notes': doctor_notes,
                    'rejected_at': timezone.now().isoformat()
                })
                
                messages.success(
                    request, 
                    'AI diagnosis rejected and alternative provided. Case marked as completed.'
                )
            
            else:
                messages.error(request, 'Invalid review decision.')
                return self.get(request, *args, **kwargs)
            
            # Save the case
            case.save()
            
            # Log the review activity
            self._log_case_review(case, review_decision, request.user)
            
            return redirect(self.success_url)
            
        except Exception as e:
            messages.error(
                request, 
                f'Error processing review: {str(e)}. Please try again.'
            )
            return self.get(request, *args, **kwargs)
    
    def _extract_ai_diagnosis_summary(self, case):
        """Extract a summary from AI diagnosis for final diagnosis field."""
        if not case.ai_diagnosis:
            return "AI diagnosis approved without modification"
        
        try:
            ai_data = json.loads(case.ai_diagnosis)
            primary_diagnoses = ai_data.get('primary_diagnoses', [])
            
            if primary_diagnoses:
                top_diagnosis = primary_diagnoses[0]
                condition = top_diagnosis.get('condition', 'Unknown condition')
                confidence = top_diagnosis.get('confidence', 0)
                return f"{condition} (AI Confidence: {confidence:.1%})"
            else:
                return "AI diagnosis approved - see detailed AI analysis"
                
        except (json.JSONDecodeError, TypeError, KeyError):
            return "AI diagnosis approved without modification"
    
    def _log_case_review(self, case, decision, doctor):
        """Log the case review for audit and analytics."""
        try:
            # You could create a CaseReviewLog model here
            # For now, we'll just update the case notes
            log_entry = {
                'action': 'case_reviewed',
                'decision': decision,
                'doctor': doctor.get_full_name(),
                'timestamp': timezone.now().isoformat(),
                'case_id': case.id
            }
            
            # Could be saved to a separate logging system
            print(f"Case Review Log: {json.dumps(log_entry)}")
            
        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Logging error: {str(e)}")


def case_detail_view(request, pk):
    """
    Display detailed view of a case for review.
    """
    case = get_object_or_404(Case, pk=pk)
    
    # Check permissions
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Parse AI diagnosis for display
    ai_diagnosis_parsed = None
    if case.ai_diagnosis:
        try:
            ai_diagnosis_parsed = json.loads(case.ai_diagnosis)
        except (json.JSONDecodeError, TypeError):
            ai_diagnosis_parsed = None
    
    context = {
        'case': case,
        'ai_diagnosis_parsed': ai_diagnosis_parsed,
    }
    
    return render(request, 'case_detail.html', context)


@login_required
def search_patients(request):
    query = request.GET.get('q', '').strip()
    print(f"Search query: {query}")  # Debug log
    
    if len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Please enter at least 2 characters'
        })
    
    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(patient_id__icontains=query) |
        Q(phone_number__icontains=query)
    )[:10]
    
    print(f"Found {patients.count()} matches")  # Debug log
    
    results = [{
        'id': patient.id,
        'patient_id': patient.patient_id,
        'name': f"{patient.first_name} {patient.last_name}",
        'phone': patient.phone_number
    } for patient in patients]
    
    return JsonResponse({
        'results': results,
        'message': '' if results else f'No patients found matching "{query}"'
    })


@login_required
def regenerate_diagnosis(request, pk):
    """
    API endpoint to regenerate AI diagnosis for a case.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        case = get_object_or_404(Case, pk=pk)
        
        # Check permissions
        if request.user.role not in ['NURSE', 'DOCTOR']:
            return JsonResponse({'error': 'Insufficient permissions'}, status=403)
        
        # Get patient data
        patient = case.patient
        symptoms = case.symptoms
        vital_signs = case.vital_signs or {}
        
        # ===== MULTI-AGENT SYSTEM WORKFLOW =====
        
        # 1. Initialize all agents
        coordinator = CoordinatorAgent()
        retriever = RetrieverAgent()
        diagnosis_agent = DiagnosisAgent()
        treatment_agent = TreatmentAgent()
        
        # 2. COORDINATOR: Route the case and assess urgency
        routing_decision = coordinator.route_case(case, symptoms, vital_signs)
        
        # 3. RETRIEVER: Search medical knowledge base
        symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
        retriever_results = retriever.search_protocols(
            query=symptoms,
            symptoms=symptom_list,
            top_k=5
        )
        
        # 4. DIAGNOSIS: Analyze symptoms
        patient_history = {
            'medical_history': patient.medical_history,
            'allergies': patient.allergies,
        }
        
        demographics = {
            'age': patient.get_age(),
            'gender': patient.get_gender_display(),
        }
        
        diagnosis_results = diagnosis_agent.analyze_symptoms(
            symptoms=symptoms,
            patient_history=patient_history,
            demographics=demographics,
            vital_signs=vital_signs,
            retriever_context=retriever_results
        )
        
        # 5. TREATMENT: Create action plan
        # Always generate treatment recommendations for all urgency levels
        treatment_results = treatment_agent.create_action_plan(
            diagnosis=diagnosis_results,
            urgency_level=routing_decision['urgency_level'],
            symptoms=symptom_list,
            red_flags=diagnosis_results.get('red_flags', []),
            emergency_conditions=diagnosis_results.get('emergency_conditions', [])
        )
        
        medication_plan = treatment_agent.recommend_medications(
            diagnosis=diagnosis_results,
            symptoms=symptom_list,
            patient_history=patient_history,
            allergies=[patient.allergies] if patient.allergies else []
        )
        treatment_results['medications'] = medication_plan
        
        # 6. COORDINATOR: Coordinate all results
        coordinated_result = coordinator.coordinate_agents(
            case,
            retriever_results,
            diagnosis_results,
            treatment_results
        )
        
        # Compile comprehensive diagnosis
        # Ensure confidence is a percentage (0-100)
        confidence_percentage = diagnosis_results['confidence_score']
        if confidence_percentage <= 1.0:
            confidence_percentage = confidence_percentage * 100
        
        comprehensive_diagnosis = {
            'multi_agent_system': 'HealthFlow DMS v1.0',
            'timestamp': timezone.now().isoformat(),
            'routing': routing_decision,
            'retriever': {
                'knowledge_base_results': retriever_results.get('results', []),
                'sources': retriever_results.get('sources', []),
                'total_documents': retriever_results.get('total_found', 0)
            },
            'diagnosis': {
                'primary_diagnosis': diagnosis_results['primary_diagnosis'],
                'confidence': round(confidence_percentage, 1),  # Ensure percentage format
                'explanation': diagnosis_results.get('explanation', ''),
                'differential_diagnoses': diagnosis_results['differential_diagnoses'],
                'red_flags': diagnosis_results['red_flags'],
                'emergency_conditions': diagnosis_results['emergency_conditions'],
                'recommended_tests': diagnosis_results['recommended_tests'],
            },
            'treatment': treatment_results,
            'coordination': coordinated_result,
        }
        
        # Update case
        case.ai_diagnosis = json.dumps(comprehensive_diagnosis, indent=2)
        case.priority = routing_decision['priority']
        case.status = routing_decision['recommended_status']
        case.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Diagnosis regenerated successfully',
            'diagnosis': diagnosis_results['primary_diagnosis']
        })
        
    except Exception as e:
        print(f"Error regenerating diagnosis: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def submit_doctor_review(request, case_id):
    """
    API endpoint for doctors to submit reviews and comments on cases.
    """
    # Check if user is a doctor
    if request.user.role != 'DOCTOR':
        return JsonResponse({
            'success': False,
            'error': 'Only doctors can submit reviews'
        }, status=403)
    
    try:
        case = get_object_or_404(Case, id=case_id)
        
        # Parse request data
        data = json.loads(request.body)
        doctor_review = data.get('doctor_review', '').strip()
        doctor_decision = data.get('doctor_decision', '')
        
        # Validate input
        if not doctor_review:
            return JsonResponse({
                'success': False,
                'error': 'Review comment is required'
            }, status=400)
        
        if doctor_decision not in ['approved', 'modified', 'rejected']:
            return JsonResponse({
                'success': False,
                'error': 'Valid decision is required (approved, modified, or rejected)'
            }, status=400)
        
        # Update case with doctor's review
        case.doctor_review = doctor_review
        case.doctor_decision = doctor_decision
        case.reviewed_by = request.user
        case.reviewed_at = timezone.now()
        
        # Update status based on decision
        if doctor_decision == 'approved':
            case.status = 'COMPLETED'
        elif doctor_decision == 'modified':
            case.status = 'IN_PROGRESS'
        elif doctor_decision == 'rejected':
            case.status = 'DOCTOR_REVIEW'
        
        case.save()

        # Notify the nurse who created the case that a doctor reviewed it
        try:
            from .models import Notification
            from django.urls import reverse

            if case.nurse:
                Notification.objects.create(
                    recipient=case.nurse,
                    actor=request.user,
                    verb=f"Doctor review on Case #{case.id}",
                    description=doctor_review,
                    target_case=case,
                    link=reverse('diagnoses:case_detail', args=[case.id])
                )
        except Exception as _e:
            # Non-fatal: log and continue
            print(f"Failed to create notification: {_e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully',
            'decision': doctor_decision
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error submitting doctor review: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read for the logged in user (AJAX).

    Returns JSON {success: True} on success.
    """
    try:
        from .models import Notification

        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read_at = timezone.now()
        notification.save()

        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Error marking notification read: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
