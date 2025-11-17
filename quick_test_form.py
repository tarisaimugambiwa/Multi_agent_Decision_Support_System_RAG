"""
Directly test if form clean methods are called
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from io import BytesIO  
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from diagnoses.forms import CaseForm
from diagnoses.models import Patient

# Create tiny test image
img = Image.new('RGB', (10, 10), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

test_file = SimpleUploadedFile(
    name='test.jpg',
    content=img_bytes.read(),
    content_type='image/jpeg'
)

print("Creating form...")
patient = Patient.objects.first()

form = CaseForm(
    data={
        'patient': patient.id,
        'symptoms': 'test',
        'vital_signs': '{}',
    },
    files={'symptom_image_file': test_file}
)

print(f"Form valid: {form.is_valid()}")
print(f"Form errors: {form.errors}")

# Check if form has attributes
print(f"\nForm attributes:")
print(f" - hasattr 'base64_image_data': {hasattr(form, 'base64_image_data')}")
print(f" - hasattr 'base64_image_filename': {hasattr(form, 'base64_image_filename')}")

if hasattr(form, 'base64_image_data'):
    print(f" - Image size: {len(form.base64_image_data)}")
    print(f" - Filename: {form.base64_image_filename}")
