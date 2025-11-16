from rest_framework.permissions import BasePermission

class HasActiveOrgLicense(BasePermission):
    def has_permission(self, request, view):
        org = getattr(request.user, "current_org", None)
        if not org:
            return False

        return org.subscription and org.subscription.is_active()
