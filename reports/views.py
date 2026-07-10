from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

from attendance.models import Attendance
from attendance.filters import AttendanceFilter
from .models import ReportLog
from .utils import export_attendance_to_excel, export_attendance_to_pdf


def _filtered_queryset(request):
    user = request.user
    base_qs = Attendance.objects.select_related('employee', 'employee__department')

    if not (user.is_admin_role or user.is_teacher_hr_role):
        base_qs = base_qs.filter(employee__user=user)

    filtered = AttendanceFilter(request.GET, queryset=base_qs)
    return filtered.qs


@login_required
def export_excel(request):
    qs = _filtered_queryset(request)
    ReportLog.objects.create(
        generated_by=request.user,
        file_type=ReportLog.FileType.EXCEL,
        start_date=request.GET.get('date_after') or None,
        end_date=request.GET.get('date_before') or None,
        record_count=qs.count(),
    )
    return export_attendance_to_excel(qs)


@login_required
def export_pdf(request):
    qs = _filtered_queryset(request)
    ReportLog.objects.create(
        generated_by=request.user,
        file_type=ReportLog.FileType.PDF,
        start_date=request.GET.get('date_after') or None,
        end_date=request.GET.get('date_before') or None,
        record_count=qs.count(),
    )
    return export_attendance_to_pdf(qs)
