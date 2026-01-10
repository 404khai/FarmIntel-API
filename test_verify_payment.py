
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from orders.views import VerifyOrderPaymentView
from orders.models import Order, OrderTransaction
from users.models import User, Farmer, Buyer
from crops.models import Crop
from transactions.models import Wallet, Transaction
from decimal import Decimal
import uuid
from unittest.mock import patch, MagicMock

def test_verify_payment():
    # 1. Setup Data
    print("Setting up data...")
    # Create Users
    buyer_user = User.objects.create_user(email=f"buyer_{uuid.uuid4()}@test.com", password="password", role="buyer")
    farmer_user = User.objects.create_user(email=f"farmer_{uuid.uuid4()}@test.com", password="password", role="farmer")
    
    farmer = Farmer.objects.create(user=farmer_user, farm_name="Test Farm")
    
    # Create Crop
    crop = Crop.objects.create(
        farmer=farmer,
        name="Test Crop",
        variety="Test Variety",
        price_per_kg=1000,
        quantity_kg=100,
    )
    
    # Create Order
    order = Order.objects.create(
        buyer=buyer_user,
        farmer=farmer,
        crop=crop,
        quantity=10,
        total_price=10000,
        status="ACCEPTED"
    )
    
    # Create OrderTransaction (Initialized)
    reference = f"ORD_{uuid.uuid4().hex[:12]}"
    OrderTransaction.objects.create(
        order=order,
        buyer=buyer_user,
        reference=reference,
        amount=10200, # Including fee
        status="INITIALIZED"
    )
    
    print(f"Created OrderTransaction with reference: {reference}")
    
    # 2. Mock Verify Transaction
    with patch('orders.views.verify_transaction') as mock_verify:
        mock_verify.return_value = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "status": "success",
                "reference": reference,
                "amount": 1020000,
                "gateway_response": "Successful"
            }
        }
        
        # 3. Call View
        factory = APIRequestFactory()
        request = factory.post('/orders/pay/verify/', {"reference": reference}, format='json')
        view = VerifyOrderPaymentView.as_view()
        response = view(request)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")
        
        # 4. Assertions
        ot = OrderTransaction.objects.get(reference=reference)
        print(f"OrderTransaction Status: {ot.status}")
        
        order.refresh_from_db()
        print(f"Order Status: {order.status}")
        
        wallet = Wallet.objects.get(farmer=farmer)
        print(f"Farmer Wallet Balance: {wallet.balance}")
        
        ft = Transaction.objects.filter(reference=reference).first()
        if ft:
            print(f"FinancialTransaction Created: {ft}")
        else:
            print("FinancialTransaction NOT Created")

if __name__ == "__main__":
    try:
        test_verify_payment()
    except Exception as e:
        print(f"Error: {e}")
