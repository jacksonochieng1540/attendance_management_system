from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in_time', 'check_out_time', 'marked_by')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__full_name')
    date_hierarchy = 'date'
    autocomplete_fields = ['employee', 'marked_by']
