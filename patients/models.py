from django.db import models
from django.conf import settings


class Patient(models.Model):
    """Patient model containing basic patient information."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    first_name = models.CharField(max_length=100, help_text='Patient first name', db_index=True)
    last_name = models.CharField(max_length=100, help_text='Patient last name', db_index=True)
    date_of_birth = models.DateField(help_text='Patient date of birth')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        help_text='Patient gender'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Patient contact phone number',
        db_index=True
    )
    address = models.TextField(
        blank=True,
        help_text='Patient residential address'
    )

    allergies = models.TextField(
        blank=True,
        help_text='Known allergies and adverse reactions'
    )

    medical_history = models.TextField(
        blank=True,
        help_text='Patient medical history and past conditions (free text)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='patient_profile',
        null=True,
        blank=True,
        help_text='Optional link to a User account for patient portal access'
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class MedicalRecord(models.Model):
    """Medical record model linking patients to healthcare providers with visit details."""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_records',
        help_text='Patient associated with this medical record'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records',
        help_text='Healthcare provider who created this record'
    )
    visit_date = models.DateTimeField(help_text='Date and time of the medical visit')
    symptoms = models.TextField(
        help_text='Patient symptoms reported during the visit'
    )
    diagnosis = models.TextField(
        blank=True,
        help_text='Medical diagnosis made during the visit'
    )
    treatment = models.TextField(
        blank=True,
        help_text='Treatment plan and medications prescribed'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes and observations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
