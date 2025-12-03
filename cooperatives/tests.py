from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Cooperative, CooperativeMembership

User = get_user_model()

class CooperativeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.farmer_user = User.objects.create_user(email='farmer@example.com', password='password', role='farmer')
        self.buyer_user = User.objects.create_user(email='buyer@example.com', password='password', role='buyer')
        self.other_farmer = User.objects.create_user(email='other_farmer@example.com', password='password', role='farmer')
        
        # Authenticate as farmer to create cooperative
        self.client.force_authenticate(user=self.farmer_user)

    def test_create_cooperative_owner_role(self):
        """Test that creating a cooperative assigns the creator as 'owner'"""
        data = {
            "name": "Green Valley Coop",
            "description": "A cooperative for organic farmers.",
            # Image is required by model but for test we can skip or mock if needed. 
            # However, the model has img = models.ImageField(), which might require a file.
            # Let's try to create without image first or provide a dummy if it fails.
            # Actually, let's check the model again. It is not blank=True.
            # We need to provide a dummy image or make it optional in model if that was intended.
            # For now, let's try to upload a simple dummy image.
        }
        
        # To avoid image issues in simple test, let's mock or use a simple file.
        # Or better, let's temporarily make image optional in model if that's acceptable, 
        # but the user didn't ask for that.
        # Let's create a dummy image content.
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        data['img'] = image

        response = self.client.post('/cooperatives/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        coop = Cooperative.objects.get(name="Green Valley Coop")
        self.assertEqual(coop.created_by, self.farmer_user)
        
        # Check membership
        membership = CooperativeMembership.objects.get(user=self.farmer_user, cooperative=coop)
        self.assertEqual(membership.role, 'owner')

    def test_farmer_join_cooperative(self):
        """Test that a farmer joining becomes 'member_farmer'"""
        # Create coop first
        coop = Cooperative.objects.create(
            name="Existing Coop", 
            created_by=self.farmer_user,
            img="path/to/img.jpg" # Dummy path for model creation
        )
        
        # Authenticate as another farmer
        self.client.force_authenticate(user=self.other_farmer)
        
        response = self.client.post(f'/cooperatives/{coop.id}/join/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        membership = CooperativeMembership.objects.get(user=self.other_farmer, cooperative=coop)
        self.assertEqual(membership.role, 'member_farmer')

    def test_buyer_join_cooperative(self):
        """Test that a buyer joining becomes 'member_buyer'"""
        # Create coop first
        coop = Cooperative.objects.create(
            name="Existing Coop 2", 
            created_by=self.farmer_user,
            img="path/to/img.jpg"
        )
        
        # Authenticate as buyer
        self.client.force_authenticate(user=self.buyer_user)
        
        response = self.client.post(f'/cooperatives/{coop.id}/join/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        membership = CooperativeMembership.objects.get(user=self.buyer_user, cooperative=coop)
        self.assertEqual(membership.role, 'member_buyer')
