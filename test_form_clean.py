"""
Test if the form's clean method exists and is callable
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

# Force reload the form module
import importlib
import diagnoses.forms
importlib.reload(diagnoses.forms)

from diagnoses.forms import CaseForm

print("\n" + "="*70)
print("TESTING FORM CLASS")
print("="*70)

# Check if clean method exists
print(f"\nForm class: {CaseForm}")
print(f"Has clean method: {hasattr(CaseForm, 'clean')}")
print(f"clean method: {CaseForm.clean}")

# Check if it's the right method
import inspect
source = inspect.getsource(CaseForm.clean)
print(f"\nFirst 200 chars of clean method source:")
print(source[:200])

# Create a form instance and call clean
from diagnoses.models import Patient
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

img = Image.new('RGB', (10, 10), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

test_file = SimpleUploadedFile('test.jpg', img_bytes.read(), content_type='image/jpeg')
patient = Patient.objects.first()

form = CaseForm(
    data={'patient': patient.id, 'symptoms': 'test', 'vital_signs': '{}'},
    files={'symptom_image_file': test_file}
)

print(f"\n{'='*70}")
print("CALLING form.is_valid()")
print(f"{'='*70}")

is_valid = form.is_valid()

print(f"\nForm is valid: {is_valid}")
print(f"Form has base64_image_data: {hasattr(form, 'base64_image_data')}")

if hasattr(form, 'base64_image_data'):
    print(f"Image size: {len(form.base64_image_data)}")
else:
    print("NO IMAGE DATA!")
    
print("\n" + "="*70)
