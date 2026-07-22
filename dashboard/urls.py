from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),

   
    path('users/', views.manage_users, name='manage_users'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('departments/', views.department_list, name='department_list'),

   
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/mark/bulk/', views.bulk_mark_attendance, name='bulk_mark_attendance'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),

   
    path('reports/', views.view_reports, name='view_reports'),
    path('reports/', include('reports.urls', namespace='reports')),
]
