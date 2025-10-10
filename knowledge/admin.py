from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import KnowledgeDocument


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for KnowledgeDocument model."""
    
    list_display = [
        'title',
        'get_document_type_badge',
        'author',
        'source',
        'get_uploaded_by',
        'publication_date',
        'upload_date',
        'get_active_status',
        'is_recent',
        'needs_review'
    ]
    
    list_filter = [
        'document_type',
        'is_active',
        'publication_date',
        'upload_date',
        'last_reviewed',
        'uploaded_by__role'
    ]
    
    search_fields = [
        'title',
        'content',
        'author',
        'source',
        'tags',
        'uploaded_by__username',
        'uploaded_by__first_name',
        'uploaded_by__last_name'
    ]
    
    ordering = ['-upload_date']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document_type', 'author', 'source', 'version')
        }),
        ('Content', {
            'fields': ('content', 'tags')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'uploaded_by', 'is_active')
        }),
        ('Review Information', {
            'fields': ('last_reviewed',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('upload_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['upload_date', 'created_at', 'updated_at']
    
    def get_document_type_badge(self, obj):
        """Display document type with colored badge."""
        colors = {
            'GUIDELINE': '#007bff',
            'PROTOCOL': '#28a745',
            'RESEARCH': '#6f42c1',
            'MANUAL': '#fd7e14',
            'CASE_STUDY': '#20c997',
            'DRUG_INFO': '#dc3545',
            'PROCEDURE': '#ffc107',
            'REFERENCE': '#6c757d',
            'TRAINING': '#e83e8c',
            'OTHER': '#adb5bd'
        }
        color = colors.get(obj.document_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_document_type_display()
        )
    get_document_type_badge.short_description = 'Type'
    get_document_type_badge.admin_order_field = 'document_type'
    
    def get_uploaded_by(self, obj):
        """Display uploader's name with role."""
        return f"{obj.uploaded_by.get_full_name() or obj.uploaded_by.username} ({obj.uploaded_by.get_role_display()})"
    get_uploaded_by.short_description = 'Uploaded By'
    get_uploaded_by.admin_order_field = 'uploaded_by__last_name'
    
    def get_active_status(self, obj):
        """Display active status with colored indicator."""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Inactive</span>'
            )
    get_active_status.short_description = 'Status'
    get_active_status.admin_order_field = 'is_active'
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by to current user if creating new document."""
        if not change:  # Creating new document
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


# Custom admin actions
@admin.action(description='Activate selected documents')
def activate_documents(modeladmin, request, queryset):
    """Activate selected documents."""
    updated = queryset.filter(is_active=False).update(is_active=True)
    modeladmin.message_user(request, f'{updated} documents activated.')


@admin.action(description='Deactivate selected documents')
def deactivate_documents(modeladmin, request, queryset):
    """Deactivate selected documents."""
    updated = queryset.filter(is_active=True).update(is_active=False)
    modeladmin.message_user(request, f'{updated} documents deactivated.')


@admin.action(description='Mark selected documents as reviewed')
def mark_reviewed(modeladmin, request, queryset):
    """Mark selected documents as reviewed today."""
    updated = queryset.update(last_reviewed=timezone.now().date())
    modeladmin.message_user(request, f'{updated} documents marked as reviewed.')


@admin.action(description='Export selected documents metadata to CSV')
def export_documents_csv(modeladmin, request, queryset):
    """Export selected documents metadata to CSV format."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="knowledge_documents.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Type', 'Author', 'Source', 'Publication Date', 
        'Upload Date', 'Uploaded By', 'Active', 'Tags', 'Version'
    ])
    
    for doc in queryset:
        writer.writerow([
            doc.title,
            doc.get_document_type_display(),
            doc.author,
            doc.source,
            doc.publication_date.strftime('%Y-%m-%d') if doc.publication_date else '',
            doc.upload_date.strftime('%Y-%m-%d %H:%M'),
            doc.uploaded_by.get_full_name() or doc.uploaded_by.username,
            'Yes' if doc.is_active else 'No',
            doc.tags,
            doc.version
        ])
    
    return response


@admin.action(description='Duplicate selected documents')
def duplicate_documents(modeladmin, request, queryset):
    """Create copies of selected documents."""
    count = 0
    for doc in queryset:
        doc.pk = None  # This will create a new instance
        doc.title = f"{doc.title} (Copy)"
        doc.uploaded_by = request.user
        doc.upload_date = timezone.now()
        doc.save()
        count += 1
    
    modeladmin.message_user(request, f'{count} documents duplicated.')


# Custom list filters
class ReviewStatusFilter(admin.SimpleListFilter):
    """Custom filter for review status."""
    title = 'Review Status'
    parameter_name = 'review_status'
    
    def lookups(self, request, model_admin):
        return (
            ('needs_review', 'Needs Review'),
            ('recently_reviewed', 'Recently Reviewed'),
            ('never_reviewed', 'Never Reviewed'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'needs_review':
            one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
            return queryset.filter(
                models.Q(last_reviewed__lt=one_year_ago) | models.Q(last_reviewed__isnull=True)
            )
        elif self.value() == 'recently_reviewed':
            thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
            return queryset.filter(last_reviewed__gte=thirty_days_ago)
        elif self.value() == 'never_reviewed':
            return queryset.filter(last_reviewed__isnull=True)


class UploadDateFilter(admin.SimpleListFilter):
    """Custom filter for upload date ranges."""
    title = 'Upload Date Range'
    parameter_name = 'upload_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(upload_date__date=now.date())
        elif self.value() == 'week':
            week_ago = now - timezone.timedelta(days=7)
            return queryset.filter(upload_date__gte=week_ago)
        elif self.value() == 'month':
            month_ago = now - timezone.timedelta(days=30)
            return queryset.filter(upload_date__gte=month_ago)
        elif self.value() == 'year':
            year_ago = now - timezone.timedelta(days=365)
            return queryset.filter(upload_date__gte=year_ago)


# Add custom filters and actions to KnowledgeDocumentAdmin
KnowledgeDocumentAdmin.list_filter = KnowledgeDocumentAdmin.list_filter + [ReviewStatusFilter, UploadDateFilter]
KnowledgeDocumentAdmin.actions = [
    activate_documents, 
    deactivate_documents, 
    mark_reviewed, 
    export_documents_csv, 
    duplicate_documents
]


# Import required modules for custom filters
from django.db import models
