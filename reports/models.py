from django.conf import settings
from django.db import models


class ReportLog(models.Model):
 

    class FileType(models.TextChoices):
        EXCEL = 'EXCEL', 'Excel (.xlsx)'
        PDF = 'PDF', 'PDF'

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='generated_reports'
    )
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        'employees.Department', on_delete=models.SET_NULL, null=True, blank=True
    )
    record_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.file_type} report by {self.generated_by} on {self.created_at:%Y-%m-%d %H:%M}'
