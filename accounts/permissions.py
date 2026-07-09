from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)


class IsAdminOrTeacherHR(BasePermission):
    """Admin and Teacher/HR accounts may access this view (e.g. mark attendance)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin_role or request.user.is_teacher_hr_role)
        )


class IsOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin_role or user.is_teacher_hr_role:
            return True
        if request.method in SAFE_METHODS:
            owner_user = getattr(getattr(obj, 'employee', obj), 'user', None)
            return owner_user_id_matches(owner_user, user)
        return False


def owner_user_id_matches(owner_user, request_user):
    return owner_user is not None and owner_user.id == request_user.id
