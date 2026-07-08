from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model so we can attach a `role` field, which drives
    permissions throughout the system:

    - ADMIN        : full access (manage users, all attendance, all reports)
    - TEACHER_HR    : can add students/employees, mark attendance, view reports
    - STUDENT_EMPLOYEE : can only view their own attendance history
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER_HR = 'TEACHER_HR', 'Teacher / HR'
        STUDENT_EMPLOYEE = 'STUDENT_EMPLOYEE', 'Student / Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT_EMPLOYEE,
        help_text='Controls what this account can see and do in the system.',
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    # Convenience helpers used in templates and views
    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher_hr_role(self):
        return self.role == self.Role.TEACHER_HR

    @property
    def is_student_employee_role(self):
        return self.role == self.Role.STUDENT_EMPLOYEE

    @property
    def can_manage_users(self):
        return self.role == self.Role.ADMIN

    @property
    def can_mark_attendance(self):
        return self.role in (self.Role.ADMIN, self.Role.TEACHER_HR)
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER_HR = 'TEACHER_HR', 'Teacher / HR'
        STUDENT_EMPLOYEE = 'STUDENT_EMPLOYEE', 'Student / Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT_EMPLOYEE,
        help_text='Controls what this account can see and do in the system.',
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    # Convenience helpers used in templates and views
    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher_hr_role(self):
        return self.role == self.Role.TEACHER_HR

    @property
    def is_student_employee_role(self):
        return self.role == self.Role.STUDENT_EMPLOYEE

    @property
    def can_manage_users(self):
        return self.role == self.Role.ADMIN

    @property
    def can_mark_attendance(self):
        return self.role in (self.Role.ADMIN, self.Role.TEACHER_HR)
