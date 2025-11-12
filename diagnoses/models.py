from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone


class Patient(models.Model):
    """Patient model representing a patient."""
    
    patient_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    # ...other fields...
    
    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"


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
    symptom_image = models.TextField(
        null=True,
        blank=True,
        help_text='Visual documentation of symptoms (base64 encoded image)'
    )
    symptom_image_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Original filename of the symptom image'
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
    
    # Treatment Plan Comments
    treatment_comments = models.TextField(
        blank=True,
        help_text='Doctor\'s comments and observations on treatment plan'
    )
    treatment_comments_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when treatment comments were added'
    )
    
    # AI Diagnosis Comments
    diagnosis_comments = models.TextField(
        blank=True,
        help_text='Doctor\'s comments and observations on AI diagnosis'
    )
    diagnosis_comments_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when diagnosis comments were added'
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


class Notification(models.Model):
    """Simple notification model for user alerts related to cases."""
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='actor_notifications',
        null=True,
        blank=True
    )
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_case = models.ForeignKey(
        'Case',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=255, blank=True, help_text='Optional relative link to view')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient} - {self.verb}"

    @property
    def is_read(self):
        return self.read_at is not None


# Signals: notify doctors when a case becomes DOCTOR_REVIEW
@receiver(pre_save, sender=Case)
def capture_previous_status(sender, instance, **kwargs):
    """Store previous status on the instance so post_save can compare."""
    if instance.pk:
        try:
            previous = sender.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except sender.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Case)
def notify_doctors_on_review_status(sender, instance, created, **kwargs):
    """Create notifications for doctors when a case enters DOCTOR_REVIEW.

    If the case has an assigned `doctor`, notify only that doctor. Otherwise
    create a notification for all users with role 'DOCTOR'.
    """
    try:
        # Only act when case newly entered DOCTOR_REVIEW
        prev = getattr(instance, '_previous_status', None)
        became_doctor_review = (instance.status == 'DOCTOR_REVIEW') and (created or prev != 'DOCTOR_REVIEW')

        if not became_doctor_review:
            return

        # Lazy import to avoid circular imports at module load
        from users.models import User

        recipients = []
        if instance.doctor:
            recipients = [instance.doctor]
        else:
            recipients = list(User.objects.filter(role='DOCTOR'))

        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                actor=instance.nurse,
                verb=f"New case requiring review: Case #{instance.id}",
                description=(instance.symptoms[:300] + '...') if instance.symptoms else '',
                target_case=instance,
                link=f"/diagnoses/{instance.id}/"
            )

    except Exception as e:
        # Non-fatal: log and continue
        print(f"Error creating review notifications: {e}")
