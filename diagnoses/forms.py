from django import forms
from .models import Case, Diagnosis


class CaseForm(forms.ModelForm):
    """Form for creating and updating medical cases"""

    class Meta:
        model = Case
        fields = [
            'patient',
            'chief_complaint',
            'symptoms',
            'vital_signs',
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'chief_complaint': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary reason for visit...'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe patient symptoms...'
            }),
            'vital_signs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter vital signs in JSON format: {"temperature": 38.5, "bp": "120/80"}'
            }),
        }


class DiagnosisForm(forms.ModelForm):
    """Form for creating and updating diagnoses"""

    class Meta:
        model = Diagnosis
        fields = [
            'diagnosis_text',
            'confidence_level',
            'urgency_level',
            'treatment_plan',
            'reasoning',
            'follow_up_required',
        ]
        widgets = {
            'diagnosis_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter primary diagnosis...'
            }),
            'confidence_level': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'urgency_level': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Recommended treatment plan...'
            }),
            'reasoning': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Clinical reasoning...'
            }),
            'follow_up_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }