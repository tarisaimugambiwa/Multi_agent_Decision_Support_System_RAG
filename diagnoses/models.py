from django.db import models
from django.conf import settings


class Case(models.Model):
    """Case model representing a diagnostic case for a patient."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('DOCTOR_REVIEW', 'Doctor Review'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent'),
        ('CRITICAL', 'Critical'),
    ]
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='cases',
        help_text='Patient associated with this diagnostic case'
    )
    nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nurse_cases',
        limit_choices_to={'role': 'NURSE'},
        help_text='Nurse who initiated the case'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='doctor_cases',
        limit_choices_to={'role': 'DOCTOR'},
        null=True,
        blank=True,
        help_text='Doctor assigned to review the case'
    )
    symptoms = models.TextField(
        help_text='Patient symptoms and chief complaints'
    )
    vital_signs = models.JSONField(
        default=dict,
        blank=True,
        help_text='Patient vital signs (temperature, blood pressure, heart rate, etc.)'
    )
    ai_diagnosis = models.TextField(
        blank=True,
        help_text='AI-generated diagnosis and recommendations'
    )
    doctor_diagnosis = models.TextField(
        blank=True,
        help_text='Doctor\'s final diagnosis and treatment plan'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Current status of the diagnostic case'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text='Priority level of the case'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the case was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the case was last updated'
    )
    
    # Doctor review fields
    doctor_review = models.TextField(
        blank=True,
        help_text='Doctor\'s review notes and decision'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reviewed_cases',
        null=True,
        blank=True,
        help_text='Doctor who reviewed this case'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the case was reviewed'
    )
    doctor_decision = models.CharField(
        max_length=20,
        choices=[
            ('approved', 'Approved'),
            ('modified', 'Modified'),
            ('rejected', 'Rejected'),
        ],
        blank=True,
        help_text='Doctor\'s decision on AI diagnosis'
    )
    final_diagnosis = models.TextField(
        blank=True,
        help_text='Final diagnosis after doctor review'
    )
    doctor_modifications = models.TextField(
        blank=True,
        help_text='JSON data for modifications made by doctor'
    )
    doctor_rejection = models.TextField(
        blank=True,
        help_text='JSON data for AI diagnosis rejection details'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Diagnostic Case'
        verbose_name_plural = 'Diagnostic Cases'
    
    def __str__(self):
        return f"Case #{self.id} - {self.patient.full_name} ({self.get_status_display()})"
    
    @property
    def is_urgent(self):
        """Check if the case is urgent or critical priority."""
        return self.priority in ['URGENT', 'CRITICAL']
    
    @property
    def days_since_created(self):
        """Calculate days since case was created."""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
    
    def assign_doctor(self, doctor):
        """Assign a doctor to the case and update status."""
        if doctor.role == 'DOCTOR':
            self.doctor = doctor
            if self.status == 'PENDING':
                self.status = 'IN_PROGRESS'
            self.save()
    
    def complete_case(self):
        """Mark the case as completed."""
        self.status = 'COMPLETED'
        self.save()
