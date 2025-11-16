from django.urls import path
from .views import (
    CreateB2BOrganizationView,
    OrganizationMembersView,
    InviteToOrganizationView,
    AcceptInvitationView,
    OrgPlanListView,
    InitializeOrgPaymentView,
    OrgPaystackWebhookView,
)

urlpatterns = [
    path("create/", CreateB2BOrganizationView.as_view()),
    path("<int:org_id>/members/", OrganizationMembersView.as_view()),
    path("invite/", InviteToOrganizationView.as_view()),
    path("invitation/accept/<uuid:token>/", AcceptInvitationView.as_view()),

    # Billing
    path("plans/", OrgPlanListView.as_view()),
    path("<int:org_id>/billing/initialize/", InitializeOrgPaymentView.as_view()),
    path("billing/webhook/", OrgPaystackWebhookView.as_view()),
]
