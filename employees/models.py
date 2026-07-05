from django.conf import settings
from django.db import models


class Department(models.Model):
    """Optional grouping, e.g. 'ICT', 'Finance', 'Grade 10', 'Engineering'."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Represents the person whose attendance is tracked — could be a
    company employee or a school student, distinguished by `category`.

    Linked 1-to-1 with a User account so the person can log in and view
    their own attendance (optional — an Employee can exist without login
    access if the Admin/HR just wants to record their attendance).
    """

    class Category(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        STUDENT = 'STUDENT', 'Student'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True,
        help_text='Optional linked login account for this person.',
    )
    employee_id = models.CharField(max_length=20, unique=True, help_text="e.g. E001, STU-2026-001")
    full_name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.EMPLOYEE)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees'
    )
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.employee_id} - {self.full_name}'

    def attendance_summary(self, start_date=None, end_date=None):
        """Quick counts of Present/Absent/Leave within an optional date range."""
        qs = self.attendance_records.all()
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        return {
            'present': qs.filter(status='PRESENT').count(),
            'absent': qs.filter(status='ABSENT').count(),
            'leave': qs.filter(status='LEAVE').count(),
            'total': qs.count(),
        }
