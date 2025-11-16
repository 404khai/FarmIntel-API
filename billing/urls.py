from django.urls import path
from .views import (
    PlanListView,
    CreateSubscriptionView,
    InitializePaymentView,
    PaystackWebhookView,
    SubscriptionDetailView,
    CancelSubscriptionView,
)

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="billing-plans"),
    path("subscriptions/create/", CreateSubscriptionView.as_view(), name="subscriptions-create"),
    path("payments/initialize/", InitializePaymentView.as_view(), name="payments-init"),
    path("webhook/paystack/", PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("subscriptions/<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("subscriptions/<int:pk>/cancel/", CancelSubscriptionView.as_view(), name="subscription-cancel"),
]
