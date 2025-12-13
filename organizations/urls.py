from django.urls import path
from .views import (
    OrgPlanListView,
    InitializeOrgPaymentView,
    OrgPaystackWebhookView,
    CreateApiKeyView,
    ListApiKeysView
)

urlpatterns = [
    path("plans/", OrgPlanListView.as_view()),
    path("<int:org_id>/billing/initialize/", InitializeOrgPaymentView.as_view()),
    path("billing/webhook/", OrgPaystackWebhookView.as_view()),
    path("<int:org_id>/api-keys/create/", CreateApiKeyView.as_view()),
    path("<int:org_id>/api-keys/", ListApiKeysView.as_view()),
]
