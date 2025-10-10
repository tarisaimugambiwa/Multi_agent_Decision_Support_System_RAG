from django.contrib import admin
from django.utils.html import format_html
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """Admin configuration for Case model."""
    
    list_display = [
        'get_case_id',
        'get_patient_name',
        'get_nurse_name',
        'get_doctor_name',
        'get_priority_badge',
        'get_status_badge',
        'get_symptoms_preview',
        'is_urgent',
        'days_since_created',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'status',
        'priority',
        'nurse__role',
        'doctor__role',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'nurse__first_name',
        'nurse__last_name',
        'nurse__username',
        'doctor__first_name',
        'doctor__last_name',
        'doctor__username',
        'symptoms',
        'ai_diagnosis',
        'doctor_diagnosis'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('Case Information', {
            'fields': ('patient', 'nurse', 'doctor', 'status', 'priority')
        }),
        ('Medical Details', {
            'fields': ('symptoms', 'vital_signs')
        }),
        ('Diagnoses', {
            'fields': ('ai_diagnosis', 'doctor_diagnosis'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_case_id(self, obj):
        """Display case ID with formatting."""
        return f"Case #{obj.id}"
    get_case_id.short_description = 'Case ID'
    get_case_id.admin_order_field = 'id'
    
    def get_patient_name(self, obj):
        """Display patient's full name."""
        return obj.patient.full_name
    get_patient_name.short_description = 'Patient'
    get_patient_name.admin_order_field = 'patient__last_name'
    
    def get_nurse_name(self, obj):
        """Display nurse's name."""
        return obj.nurse.get_full_name() or obj.nurse.username
    get_nurse_name.short_description = 'Nurse'
    get_nurse_name.admin_order_field = 'nurse__last_name'
    
    def get_doctor_name(self, obj):
        """Display doctor's name or 'Not Assigned'."""
        if obj.doctor:
            return obj.doctor.get_full_name() or obj.doctor.username
        return "Not Assigned"
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'doctor__last_name'
    
    def get_priority_badge(self, obj):
        """Display priority with colored badge."""
        colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'URGENT': '#dc3545',
            'CRITICAL': '#6f42c1'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    get_priority_badge.short_description = 'Priority'
    get_priority_badge.admin_order_field = 'priority'
    
    def get_status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'PENDING': '#6c757d',
            'IN_PROGRESS': '#007bff',
            'DOCTOR_REVIEW': '#fd7e14',
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'
    
    def get_symptoms_preview(self, obj):
        """Display truncated symptoms for list view."""
        if obj.symptoms:
            return obj.symptoms[:60] + "..." if len(obj.symptoms) > 60 else obj.symptoms
        return "-"
    get_symptoms_preview.short_description = 'Symptoms'


# Custom admin actions
@admin.action(description='Assign selected cases to doctor')
def assign_to_doctor(modeladmin, request, queryset):
    """Bulk assign cases to a doctor."""
    # This would typically open a form to select doctor
    # For now, we'll just update status to indicate doctor review needed
    updated = queryset.filter(status='PENDING').update(status='DOCTOR_REVIEW')
    modeladmin.message_user(request, f'{updated} cases moved to doctor review.')


@admin.action(description='Mark selected cases as completed')
def mark_completed(modeladmin, request, queryset):
    """Mark selected cases as completed."""
    updated = queryset.exclude(status='COMPLETED').update(status='COMPLETED')
    modeladmin.message_user(request, f'{updated} cases marked as completed.')


@admin.action(description='Export selected cases to CSV')
def export_cases_csv(modeladmin, request, queryset):
    """Export selected cases to CSV format."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cases.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Case ID', 'Patient', 'Nurse', 'Doctor', 'Priority', 'Status', 
        'Symptoms', 'Created Date', 'Days Since Created'
    ])
    
    for case in queryset:
        writer.writerow([
            f"Case #{case.id}",
            case.patient.full_name,
            case.nurse.get_full_name() or case.nurse.username,
            case.doctor.get_full_name() if case.doctor else "Not Assigned",
            case.get_priority_display(),
            case.get_status_display(),
            case.symptoms[:100],
            case.created_at.strftime('%Y-%m-%d %H:%M'),
            case.days_since_created
        ])
    
    return response


# Add custom actions to CaseAdmin
CaseAdmin.actions = [assign_to_doctor, mark_completed, export_cases_csv]
