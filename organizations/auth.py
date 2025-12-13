from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("X-API-Key")
        if not token:
            return None
        try:
            apikey = ApiKey.objects.select_related("organization", "organization__created_by").get(key=token, active=True)
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key")
        user = apikey.organization.created_by
        return (user, apikey)

