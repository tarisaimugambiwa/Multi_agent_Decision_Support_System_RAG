from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Facility, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_active',
        'date_joined'
    ]
    
    list_filter = [
        'role',
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined'
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name'
    ]
    
    ordering = ['-date_joined']
    
    # Add role field to the existing fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Medical System Info', {
            'fields': ('role',)
        }),
    )
    
    # Add role field to add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Medical System Info', {
            'fields': ('role',)
        }),
    )


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    """Admin configuration for Facility model."""
    
    list_display = [
        'name',
        'phone',
        'email',
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'name',
        'address',
        'phone',
        'email'
    ]
    
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    
    list_display = [
        'user',
        'get_user_role',
        'facility',
        'department',
        'license_number',
        'created_at'
    ]
    
    list_filter = [
        'user__role',
        'facility',
        'department',
        'created_at'
    ]
    
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'facility__name',
        'department',
        'license_number'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('User & Facility', {
            'fields': ('user', 'facility')
        }),
        ('Professional Information', {
            'fields': ('department', 'license_number')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user_role(self, obj):
        """Display user's role in the list view."""
        return obj.user.get_role_display()
    get_user_role.short_description = 'Role'
    get_user_role.admin_order_field = 'user__role'


# Inline admin for UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile in User admin."""
    model = UserProfile
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


# Update UserAdmin to include UserProfile inline
UserAdmin.inlines = [UserProfileInline]
