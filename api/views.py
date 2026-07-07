from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.permissions import IsAdmin, IsAdminOrTeacherHR, IsOwnerOrStaff
from employees.models import Department, Employee
from attendance.models import Attendance
from attendance.filters import AttendanceFilter

from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer,
    DepartmentSerializer, EmployeeSerializer, AttendanceSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """POST {username, password} -> {access, refresh}. Payload includes role/full_name."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """Public sign-up endpoint. New accounts default to STUDENT_EMPLOYEE role."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrTeacherHR]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Admin/HR: full CRUD over all employees.
    Student/Employee: read-only access to their own linked record.
    """
    serializer_class = EmployeeSerializer
    filterset_fields = ['category', 'department', 'is_active']
    search_fields = ['employee_id', 'full_name', 'email']
    ordering_fields = ['employee_id', 'full_name', 'date_joined']

    def get_permissions(self):
        if self.action in ('list', 'create', 'update', 'partial_update', 'destroy'):
            return [IsAdminOrTeacherHR()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Employee.objects.select_related('department', 'user')
        if user.is_admin_role or user.is_teacher_hr_role:
            return qs
        return qs.filter(user=user)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Admin/HR: mark & manage attendance for anyone.
    Student/Employee: read-only access to their own attendance history.
    """
    serializer_class = AttendanceSerializer
    filterset_class = AttendanceFilter
    search_fields = ['employee__employee_id', 'employee__full_name', 'remarks']
    ordering_fields = ['date', 'status', 'created_at']
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('employee', 'employee__department', 'marked_by')
        if user.is_admin_role or user.is_teacher_hr_role:
            return qs
        return qs.filter(employee__user=user)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminOrTeacherHR()]
        return [IsOwnerOrStaff()]

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacherHR])
    def summary(self, request):
        """GET /api/v1/attendance/summary/?date_after=...&date_before=... -> counts by status."""
        qs = self.filter_queryset(self.get_queryset())
        data = {
            'total': qs.count(),
            'present': qs.filter(status=Attendance.Status.PRESENT).count(),
            'absent': qs.filter(status=Attendance.Status.ABSENT).count(),
            'leave': qs.filter(status=Attendance.Status.LEAVE).count(),
        }
        return Response(data, status=status.HTTP_200_OK)
