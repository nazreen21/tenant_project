from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "SUPERADMIN"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ADMIN"


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ["ADMIN", "MANAGER"]


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "STAFF"