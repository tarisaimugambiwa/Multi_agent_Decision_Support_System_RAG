from django.contrib import admin
from .models import Patient, MedicalRecord


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin configuration for Patient model."""
    
    list_display = [
        'full_name',
        'date_of_birth',
        'get_age',
        'gender',
        'phone_number',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'gender',
        'date_of_birth',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'first_name',
        'last_name',
        'phone_number',
        'address'
    ]
    
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Medical Information', {
            'fields': ('medical_history', 'allergies'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_age(self, obj):
        """Display patient's current age."""
        return f"{obj.get_age()} years"
    get_age.short_description = 'Age'
    get_age.admin_order_field = 'date_of_birth'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MedicalRecord model."""
    
    list_display = [
        'get_patient_name',
        'get_provider_name',
        'visit_date',
        'get_symptoms_preview',
        'get_diagnosis_preview',
        'created_at'
    ]
    
    list_filter = [
        'visit_date',
        'user__role',
        'patient__gender',
        'created_at'
    ]
    
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'user__first_name',
        'user__last_name',
        'user__username',
        'symptoms',
        'diagnosis',
        'treatment'
    ]
    
    ordering = ['-visit_date']
    
    fieldsets = (
        ('Record Information', {
            'fields': ('patient', 'user', 'visit_date')
        }),
        ('Medical Details', {
            'fields': ('symptoms', 'diagnosis', 'treatment', 'notes')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        """Display patient's full name."""
        return obj.patient.full_name
    get_patient_name.short_description = 'Patient'
    get_patient_name.admin_order_field = 'patient__last_name'
    
    def get_provider_name(self, obj):
        """Display healthcare provider's name with role."""
        return f"{obj.user.get_full_name()} ({obj.user.get_role_display()})"
    get_provider_name.short_description = 'Provider'
    get_provider_name.admin_order_field = 'user__last_name'
    
    def get_symptoms_preview(self, obj):
        """Display truncated symptoms for list view."""
        if obj.symptoms:
            return obj.symptoms[:50] + "..." if len(obj.symptoms) > 50 else obj.symptoms
        return "-"
    get_symptoms_preview.short_description = 'Symptoms'
    
    def get_diagnosis_preview(self, obj):
        """Display truncated diagnosis for list view."""
        if obj.diagnosis:
            return obj.diagnosis[:50] + "..." if len(obj.diagnosis) > 50 else obj.diagnosis
        return "-"
    get_diagnosis_preview.short_description = 'Diagnosis'


# Inline admin for MedicalRecord in Patient admin
class MedicalRecordInline(admin.TabularInline):
    """Inline admin for MedicalRecord in Patient admin."""
    model = MedicalRecord
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['user', 'visit_date', 'symptoms', 'diagnosis', 'treatment']
    
    def get_queryset(self, request):
        """Optimize queryset for inline display."""
        return super().get_queryset(request).select_related('user')


# Update PatientAdmin to include MedicalRecord inline
PatientAdmin.inlines = [MedicalRecordInline]


# Custom admin actions
@admin.action(description='Export selected patients to CSV')
def export_patients_csv(modeladmin, request, queryset):
    """Export selected patients to CSV format."""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Date of Birth', 'Gender', 'Phone', 'Age'])
    
    for patient in queryset:
        writer.writerow([
            patient.first_name,
            patient.last_name,
            patient.date_of_birth,
            patient.get_gender_display(),
            patient.phone_number,
            patient.get_age()
        ])
    
    return response


# Add custom actions to PatientAdmin
PatientAdmin.actions = [export_patients_csv]
