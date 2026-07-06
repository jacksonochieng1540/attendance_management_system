from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Q

from employees.models import Employee, Department
from employees.forms import EmployeeForm, DepartmentForm, EmployeeSearchForm
from attendance.models import Attendance
from attendance.forms import AttendanceForm, BulkAttendanceForm, AttendanceFilterForm
from attendance.filters import AttendanceFilter
from .forms import DashboardLoginForm, StaffUserCreateForm, StaffUserUpdateForm

User = get_user_model()


def _is_admin(user):
    return user.is_authenticated and user.is_admin_role


def _is_staff_role(user):
    return user.is_authenticated and (user.is_admin_role or user.is_teacher_hr_role)


class DashboardLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = DashboardLoginForm
    redirect_authenticated_user = True


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard:login')

@login_required
def home(request):
    user = request.user
    today = timezone.localdate()

    if _is_staff_role(user):
        today_qs = Attendance.objects.filter(date=today)
        context = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'today_present': today_qs.filter(status='PRESENT').count(),
            'today_absent': today_qs.filter(status='ABSENT').count(),
            'today_leave': today_qs.filter(status='LEAVE').count(),
            'departments': Department.objects.annotate(emp_count=Count('employees')),
            'recent_attendance': Attendance.objects.select_related('employee').order_by('-created_at')[:10],
        }
    else:
        employee = getattr(user, 'employee_profile', None)
        my_records = Attendance.objects.filter(employee=employee).order_by('-date') if employee else Attendance.objects.none()
        context = {
            'employee': employee,
            'my_recent_attendance': my_records[:15],
            'my_summary': employee.attendance_summary() if employee else None,
        }

    context['today'] = today
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def manage_users(request):
    users = User.objects.all().order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q))
    return render(request, 'dashboard/manage_users.html', {'users': users, 'q': q})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_create(request):
    if request.method == 'POST':
        form = StaffUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User account created successfully.')
            return redirect('dashboard:manage_users')
    else:
        form = StaffUserCreateForm()
    return render(request, 'dashboard/user_form.html', {'form': form, 'title': 'Add User'})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'User account updated.')
            return redirect('dashboard:manage_users')
    else:
        form = StaffUserUpdateForm(instance=user_obj)
    return render(request, 'dashboard/user_form.html', {'form': form, 'title': f'Edit {user_obj.username}'})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User account deleted.')
        return redirect('dashboard:manage_users')
    return render(request, 'dashboard/confirm_delete.html', {'object': user_obj, 'title': 'Delete User'})


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def employee_list(request):
    form = EmployeeSearchForm(request.GET or None)
    qs = Employee.objects.select_related('department').order_by('employee_id')
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        department = form.cleaned_data.get('department')
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(employee_id__icontains=q))
        if category:
            qs = qs.filter(category=category)
        if department:
            qs = qs.filter(department=department)
    return render(request, 'dashboard/employee_list.html', {'employees': qs, 'form': form})


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee/Student added successfully.')
            return redirect('dashboard:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'dashboard/employee_form.html', {'form': form, 'title': 'Add Employee / Student'})


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee/Student updated.')
            return redirect('dashboard:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'dashboard/employee_form.html', {'form': form, 'title': f'Edit {employee.full_name}'})


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee/Student removed.')
        return redirect('dashboard:employee_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': employee, 'title': 'Delete Employee'})


@login_required
@user_passes_test(_is_admin, login_url='dashboard:home')
def department_list(request):
    departments = Department.objects.annotate(emp_count=Count('employees')).order_by('name')
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added.')
            return redirect('dashboard:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'dashboard/department_list.html', {'departments': departments, 'form': form})

@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def mark_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            attendance.save()
            messages.success(
                request,
                f'Attendance marked: {attendance.employee.full_name} - {attendance.get_status_display()} on {attendance.date}.'
            )
            return redirect('dashboard:mark_attendance')
    else:
        form = AttendanceForm()

    today = timezone.localdate()
    todays_records = Attendance.objects.filter(date=today).select_related('employee').order_by('employee__employee_id')
    return render(request, 'dashboard/mark_attendance.html', {
        'form': form, 'todays_records': todays_records, 'today': today,
    })


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def bulk_mark_attendance(request):
    """
    Quickly mark everyone in a department as Present (default_status) for a date,
    then staff can flip individual exceptions afterwards from Mark Attendance.
    """
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            department = form.cleaned_data['department']
            default_status = form.cleaned_data['default_status']

            employees = Employee.objects.filter(is_active=True)
            if department:
                employees = employees.filter(department=department)

            created_count = 0
            for employee in employees:
                _, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=date,
                    defaults={'status': default_status, 'marked_by': request.user},
                )
                if created:
                    created_count += 1

            messages.success(request, f'Bulk attendance created for {created_count} employee(s) on {date}.')
            return redirect('dashboard:mark_attendance')
    else:
        form = BulkAttendanceForm()
    return render(request, 'dashboard/bulk_mark_attendance.html', {'form': form})


@login_required
@user_passes_test(_is_staff_role, login_url='dashboard:home')
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record updated.')
            return redirect('dashboard:mark_attendance')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'dashboard/mark_attendance.html', {
        'form': form, 'editing': True, 'todays_records': [], 'today': timezone.localdate(),
    })

@login_required
def view_reports(request):
    user = request.user
    base_qs = Attendance.objects.select_related('employee', 'employee__department')

    if not _is_staff_role(user):
        base_qs = base_qs.filter(employee__user=user)

    filter_form = AttendanceFilterForm(request.GET or None)
    django_filter_params = {}
    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd.get('start_date'):
            django_filter_params['date_after'] = cd['start_date']
        if cd.get('end_date'):
            django_filter_params['date_before'] = cd['end_date']
        if cd.get('employee'):
            django_filter_params['employee_id'] = cd['employee'].employee_id
        if cd.get('department'):
            django_filter_params['department'] = cd['department'].id
        if cd.get('status'):
            django_filter_params['status'] = cd['status']

    records = AttendanceFilter(django_filter_params, queryset=base_qs).qs.order_by('-date')

    export_query = request.GET.urlencode()

    return render(request, 'dashboard/view_reports.html', {
        'filter_form': filter_form,
        'records': records,
        'export_query': export_query,
    })
