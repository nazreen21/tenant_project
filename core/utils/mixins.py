

class TenantScopedQuerysetMixin:

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role == "SUPERADMIN":
            return qs

        return qs.filter(tenant=user.tenant)