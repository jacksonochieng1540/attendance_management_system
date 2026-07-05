from django.contrib import admin
from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'category', 'department', 'is_active', 'date_joined')
    list_filter = ('category', 'department', 'is_active')
    search_fields = ('employee_id', 'full_name', 'email')
    autocomplete_fields = ['user']
