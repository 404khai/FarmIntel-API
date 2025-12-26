from django.urls import path
from .views import FarmerWalletView, TransactionListView

urlpatterns = [
    path("wallet/", FarmerWalletView.as_view(), name="farmer-wallet"),
    path("history/", TransactionListView.as_view(), name="transaction-history"),
]
