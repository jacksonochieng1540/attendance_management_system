import django_filters
from .models import Attendance


class AttendanceFilter(django_filters.FilterSet):

    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    employee_id = django_filters.CharFilter(field_name='employee__employee_id', lookup_expr='icontains')
    department = django_filters.NumberFilter(field_name='employee__department__id')
    status = django_filters.ChoiceFilter(choices=Attendance.Status.choices)

    class Meta:
        model = Attendance
        fields = ['date_after', 'date_before', 'employee_id', 'department', 'status']
