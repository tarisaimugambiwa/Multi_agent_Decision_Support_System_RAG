from django.db import models
from django.conf import settings
from django.utils import timezone


class KnowledgeDocument(models.Model):
    """Knowledge document model for storing medical knowledge base content."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('GUIDELINE', 'Clinical Guideline'),
        ('PROTOCOL', 'Medical Protocol'),
        ('RESEARCH', 'Research Paper'),
        ('MANUAL', 'Medical Manual'),
        ('CASE_STUDY', 'Case Study'),
        ('DRUG_INFO', 'Drug Information'),
        ('PROCEDURE', 'Medical Procedure'),
        ('REFERENCE', 'Reference Material'),
        ('TRAINING', 'Training Material'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(
        max_length=255,
        help_text='Title of the knowledge document'
    )
    content = models.TextField(
        help_text='Full content of the document'
    )
    document_type = models.CharField(
        max_length=15,
        choices=DOCUMENT_TYPE_CHOICES,
        default='REFERENCE',
        help_text='Type/category of the document'
    )
    source = models.CharField(
        max_length=255,
        blank=True,
        help_text='Source or origin of the document (journal, organization, etc.)'
    )
    author = models.CharField(
        max_length=255,
        blank=True,
        help_text='Author(s) of the document'
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        help_text='Original publication date of the document'
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time when the document was uploaded to the system'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        help_text='User who uploaded this document'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the document is currently active and available for use'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated tags for easier searching'
    )
    version = models.CharField(
        max_length=20,
        blank=True,
        help_text='Version number of the document'
    )
    last_reviewed = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the document was last reviewed for accuracy'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Knowledge Document'
        verbose_name_plural = 'Knowledge Documents'
        indexes = [
            models.Index(fields=['document_type', 'is_active']),
            models.Index(fields=['title']),
            models.Index(fields=['upload_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
    
    @property
    def is_recent(self):
        """Check if document was uploaded in the last 30 days."""
        return (timezone.now() - self.upload_date).days <= 30
    
    @property
    def needs_review(self):
        """Check if document needs review (older than 1 year since last review)."""
        if not self.last_reviewed:
            return True
        return (timezone.now().date() - self.last_reviewed).days > 365
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_from_list(self, tag_list):
        """Set tags from a list of strings."""
        self.tags = ', '.join(tag_list)
    
    def deactivate(self):
        """Deactivate the document."""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Activate the document."""
        self.is_active = True
        self.save()
    
    def mark_reviewed(self):
        """Mark the document as reviewed today."""
        self.last_reviewed = timezone.now().date()
        self.save()
