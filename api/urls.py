from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('employees', views.EmployeeViewSet, basename='employee')
router.register('attendance', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),

    
    path('', include(router.urls)),
]
