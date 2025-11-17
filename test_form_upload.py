"""
Test the form upload process by simulating file upload
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from diagnoses.forms import CaseForm
from diagnoses.models import Case, Patient
from django.contrib.auth.models import User

print("\n" + "="*70)
print("TESTING FORM IMAGE UPLOAD PROCESS")
print("="*70)

# Create a test image
img = Image.new('RGB', (400, 400), color='white')
from PIL import ImageDraw
draw = ImageDraw.Draw(img)
draw.rectangle([50, 50, 350, 350], fill='lightblue', outline='blue', width=5)
draw.text((100, 180), "FORM UPLOAD TEST", fill='black')

img_bytes = BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Create a SimpleUploadedFile (simulates file upload)
test_file = SimpleUploadedFile(
    name='form_test_image.jpg',
    content=img_bytes.read(),
    content_type='image/jpeg'
)

print(f"\n1. Created test file:")
print(f"   - Name: {test_file.name}")
print(f"   - Size: {test_file.size} bytes")

# Get patient for testing
patient = Patient.objects.first()
print(f"\n2. Using patient: {patient}")

# Create form data
form_data = {
    'patient': patient.id,
    'symptoms': 'Test symptom from form',
    'vital_signs': '{"temperature": 37.5}',
}

form_files = {
    'symptom_image_file': test_file,
}

print(f"\n3. Creating form with:")
print(f"   - Patient ID: {form_data['patient']}")
print(f"   - Symptoms: {form_data['symptoms']}")
print(f"   - Image file: {form_files['symptom_image_file'].name}")

# Create the form
form = CaseForm(data=form_data, files=form_files)

print(f"\n4. Form validation:")
print(f"   - Form is valid: {form.is_valid()}")

if not form.is_valid():
    print(f"   - Form errors: {form.errors}")
    print(f"   - Non-field errors: {form.non_field_errors()}")
else:
    print(f"   - ✅ Form is valid!")
    print(f"   - Has base64_image_data: {hasattr(form, 'base64_image_data')}")
    if hasattr(form, 'base64_image_data'):
        print(f"   - Image size: {len(form.base64_image_data)} chars (base64)")
        print(f"   - Filename: {form.base64_image_filename}")
    else:
        print(f"   - ❌ NO IMAGE DATA ON FORM!")

print("\n" + "="*70)
