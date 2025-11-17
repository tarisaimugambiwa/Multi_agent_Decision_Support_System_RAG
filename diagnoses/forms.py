from django import forms
from .models import Case
import base64


class CaseForm(forms.ModelForm):
    """Form for creating and updating medical cases"""
    
    # Add a file field for image upload (not directly mapped to model)
    symptom_image_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        label='Symptom Image'
    )

    class Meta:
        model = Case
        fields = [
            'patient',
            'symptoms',
            'vital_signs',
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select form-select-lg'
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
    
    def save(self, commit=True):
        """Override save to handle image upload."""
        instance = super().save(commit=False)
        
        # Handle image upload
        image_file = self.files.get('symptom_image_file')
        if image_file:
            # Convert to base64
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Store in model
            instance.symptom_image = base64_image
            instance.symptom_image_filename = image_file.name
        
        if commit:
            instance.save()
        
        return instance