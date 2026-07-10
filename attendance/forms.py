from django import forms
from django.utils import timezone
from .models import Attendance
from employees.models import Employee, Department

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'check_in_time', 'check_out_time', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
            'remarks': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.localdate()


class BulkAttendanceForm(forms.Form):
    """Mark attendance for every active employee/student in one department on one date."""

    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.localdate)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='All Departments')
    default_status = forms.ChoiceField(choices=Attendance.Status.choices, initial=Attendance.Status.PRESENT)


class AttendanceFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    employee = forms.ModelChoiceField(required=False, queryset=Employee.objects.all(), empty_label='All')
    department = forms.ModelChoiceField(required=False, queryset=Department.objects.all(), empty_label='All Departments')
    status = forms.ChoiceField(required=False, choices=[('', 'All Statuses')] + list(Attendance.Status.choices))
