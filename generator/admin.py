# generator/admin.py
from django.contrib import admin
from .models import CompanyInfo, Employee
from .models import CompanyInfo, Employee, BusinessCard


class BusinessCardInline(admin.StackedInline):
    model = BusinessCard
    can_delete = False
    verbose_name_plural = 'Business Card Details'
    fk_name = 'employee'
    fields = ('personal_phone', 'personal_email', 'website_url')



@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    # Add the new fields here to make them editable
    list_display = ('name', 'email', 'phone', 'website')
    fieldsets = (
        (None, {'fields': ('name', 'logo', 'tagline')}),
        ('Contact Information', {'fields': ('address', 'phone', 'email', 'website','tin_number')}),
        ('Social Media', {'fields': ('linkedin_url', 'instagram_url', 'facebook_url')}),
        ('Bank Remittance Details', {
            'fields': ('bank_name', 'account_number', 'account_name')
        }),
    )

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'employee_id', 'job_title', 'department')
    search_fields = ('full_name', 'employee_id', 'department')
    inlines = (BusinessCardInline,)