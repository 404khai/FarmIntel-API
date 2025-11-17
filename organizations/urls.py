from django.urls import path
from .views import (
    OrgPlanListView,
    InitializeOrgPaymentView,
    OrgPaystackWebhookView
)

urlpatterns = [
    path("plans/", OrgPlanListView.as_view()),
    path("<int:org_id>/billing/initialize/", InitializeOrgPaymentView.as_view()),
    path("billing/webhook/", OrgPaystackWebhookView.as_view()),
]
