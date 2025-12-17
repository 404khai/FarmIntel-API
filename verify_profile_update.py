import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Farmer, Buyer

User = get_user_model()

def verify_profile_update():
    client = APIClient()
    email = "testfarmer@example.com"
    password = "testpassword123"

    # Cleanup previous runs
    User.objects.filter(email=email).delete()

    print("Creating test user (Farmer)...")
    user = User.objects.create_user(email=email, password=password, role='farmer')
    Farmer.objects.create(user=user) # Ensure profile exists

    # Force authentication
    client.force_authenticate(user=user)

    # Test updating Farmer profile
    print("Testing Farmer profile update...")
    payload = {
        "first_name": "Farmer",
        "last_name": "Joe",
        "farm_name": "Joe's Farm",
        "crops": ["Corn", "Wheat"]
    }
    
    response = client.patch('/users/me', data=payload, format='json')
    
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.data)
        return

    # Refresh from DB
    user.refresh_from_db()
    farmer = user.farmer
    
    if farmer.farm_name == "Joe's Farm" and "Corn" in farmer.crops:
         print("SUCCESS: Farmer profile updated correctly!")
    else:
         print("FAILED: Farmer profile not updated.")
         print(f"Farm Name: {farmer.farm_name}")
         print(f"Crops: {farmer.crops}")

    # Test Buyer
    print("\nTesting Buyer profile update...")
    email_buyer = "testbuyer@example.com"
    User.objects.filter(email=email_buyer).delete()
    
    user_buyer = User.objects.create_user(email=email_buyer, password=password, role='buyer')
    Buyer.objects.create(user=user_buyer)
    
    client.force_authenticate(user=user_buyer)
    
    payload_buyer = {
        "company_name": "Big Buyer Corp"
    }
    
    response = client.patch('/auth/profile/update/', data=payload_buyer, format='json')
    
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.data)
        return

    user_buyer.refresh_from_db()
    buyer = user_buyer.buyer
    
    if buyer.company_name == "Big Buyer Corp":
        print("SUCCESS: Buyer profile updated correctly!")
    else:
        print("FAILED: Buyer profile not updated.")
        print(f"Company Name: {buyer.company_name}")

    # Cleanup
    print("\nCleaning up...")
    User.objects.filter(email=email).delete()
    User.objects.filter(email=email_buyer).delete()

if __name__ == "__main__":
    verify_profile_update()
