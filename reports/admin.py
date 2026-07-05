from django.contrib import admin
from .models import ReportLog


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = ('file_type', 'generated_by', 'start_date', 'end_date', 'record_count', 'created_at')
    list_filter = ('file_type', 'created_at')
    readonly_fields = [f.name for f in ReportLog._meta.fields]

    def has_add_permission(self, request):
        return False
