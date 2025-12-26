import os
import django
from decouple import config

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from detector.services import TreatmentService

print("Testing TreatmentService...")
result = TreatmentService.get_treatment_plan("Tomato_Early_blight", 0.95)
print("Result:", result)
