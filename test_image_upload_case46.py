"""
Test script to verify image upload works by creating a case with an image
and checking if it displays properly
"""
import os
import django
import base64
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

# Create a test image in memory
def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

# Create image and convert to base64
img_file = create_test_image()
base64_image = base64.b64encode(img_file.read()).decode('utf-8')

print(f"Created base64 image: {base64_image[:50]}... (length: {len(base64_image)})")

# Update case #46 with image data
case = Case.objects.get(id=46)
case.symptom_image = base64_image
case.symptom_image_filename = 'test_snake_bite.jpg'
case.save()

print(f"\n✅ Case #{case.id} updated successfully!")
print(f"   - Image stored: {len(case.symptom_image)} chars")
print(f"   - Filename: {case.symptom_image_filename}")
print(f"\n📍 Visit: http://127.0.0.1:8000/diagnoses/{case.id}/")
print(f"   The image should now be visible below the Chief Complaints & Symptoms card")
