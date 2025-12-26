from django.urls import path
from .views import (
    PlaceOrderView, OrderListView, OrderActionView, 
    InitializeOrderPaymentView, VerifyOrderPaymentView
)

urlpatterns = [
    path("place/", PlaceOrderView.as_view(), name="place-order"),
    path("list/", OrderListView.as_view(), name="list-orders"),
    path("<int:pk>/action/", OrderActionView.as_view(), name="order-action"),
    path("<int:pk>/pay/initialize/", InitializeOrderPaymentView.as_view(), name="initialize-order-payment"),
    path("pay/verify/", VerifyOrderPaymentView.as_view(), name="verify-order-payment"),
]
