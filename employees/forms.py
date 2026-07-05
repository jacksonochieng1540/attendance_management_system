from django import forms
from .models import Employee, Department


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'full_name', 'category', 'department',
            'email', 'phone_number', 'is_active',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'placeholder': 'e.g. E001'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+254 7XX XXX XXX'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']


class EmployeeSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(
        attrs={'placeholder': 'Search by name or ID'}))
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + list(Employee.Category.choices),
    )
    department = forms.ModelChoiceField(
        required=False, queryset=Department.objects.all(), empty_label='All Departments'
    )
