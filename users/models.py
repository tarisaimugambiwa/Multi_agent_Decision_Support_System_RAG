from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom User model extending AbstractUser with role field."""
    
    ROLE_CHOICES = [
        ('NURSE', 'Nurse'),
        ('DOCTOR', 'Doctor'),
        ('EXPERT', 'Expert'),
        ('PATIENT', 'Patient'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='NURSE',
        help_text='User role in the medical system'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Facility(models.Model):
    """Medical facility model."""
    
    name = models.CharField(max_length=255, help_text='Name of the medical facility')
    address = models.TextField(help_text='Address of the facility')
    phone = models.CharField(max_length=20, blank=True, help_text='Contact phone number')
    email = models.EmailField(blank=True, help_text='Contact email address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Facilities'
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """User profile model linking User to Facility."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='User associated with this profile'
    )
    facility = models.OneToOneField(
        Facility,
        on_delete=models.CASCADE,
        related_name='user_profile',
        help_text='Facility where the user works'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department within the facility'
    )
    license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Professional license number'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.facility.name}"
