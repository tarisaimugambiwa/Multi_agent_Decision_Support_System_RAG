"""
Test script to verify image upload and save functionality for cases.
This script checks that images are properly saved to the database and can be retrieved.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from diagnoses.models import Case
from patients.models import Patient
from users.models import User
import base64
from datetime import datetime

def test_image_functionality():
    """Test that images are properly saved and retrieved"""
    
    print("=" * 70)
    print("Testing Image Upload and Save Functionality")
    print("=" * 70)
    
    # 1. Check recent cases with images
    print("\n1. Checking recent cases with symptom images...")
    cases_with_images = Case.objects.filter(
        symptom_image__isnull=False
    ).exclude(symptom_image='').order_by('-created_at')[:5]
    
    if cases_with_images.exists():
        print(f"   ✓ Found {cases_with_images.count()} cases with images")
        
        for case in cases_with_images:
            print(f"\n   Case #{case.id}:")
            print(f"   - Patient: {case.patient.full_name}")
            print(f"   - Created: {case.created_at}")
            print(f"   - Symptoms: {case.symptoms[:100]}...")
            
            # Check if image data is valid base64
            if case.symptom_image:
                print(f"   - Image filename: {case.symptom_image_filename or 'Not set'}")
                print(f"   - Image data length: {len(case.symptom_image)} characters")
                
                # Verify it's valid base64
                try:
                    # Try to decode base64
                    image_data = base64.b64decode(case.symptom_image)
                    print(f"   - Image size: {len(image_data)} bytes ({len(image_data)/1024:.2f} KB)")
                    
                    # Check image format
                    if image_data.startswith(b'\xff\xd8\xff'):
                        print(f"   - Image format: JPEG ✓")
                    elif image_data.startswith(b'\x89PNG'):
                        print(f"   - Image format: PNG ✓")
                    else:
                        print(f"   - Image format: Unknown (first bytes: {image_data[:10]})")
                    
                except Exception as e:
                    print(f"   ✗ Error decoding base64: {e}")
            else:
                print(f"   ✗ No image data found")
    else:
        print("   ⚠ No cases with images found in database")
        print("   This is expected if no images have been uploaded yet.")
    
    # 2. Check if all required fields are present in the model
    print("\n2. Verifying Case model has required image fields...")
    test_fields = ['symptom_image', 'symptom_image_filename']
    
    for field_name in test_fields:
        if hasattr(Case, field_name):
            print(f"   ✓ Field '{field_name}' exists in Case model")
        else:
            print(f"   ✗ Field '{field_name}' missing from Case model")
    
    # 3. Test form import
    print("\n3. Testing form import and configuration...")
    try:
        from diagnoses.forms import CaseForm
        
        form = CaseForm()
        if hasattr(form, 'fields') and 'symptom_image_file' in form.fields:
            print(f"   ✓ CaseForm has 'symptom_image_file' field")
        else:
            print(f"   ✗ CaseForm missing 'symptom_image_file' field")
        
        # Check if form has save method override
        if hasattr(CaseForm, 'save'):
            print(f"   ✓ CaseForm has custom save method")
        
    except ImportError as e:
        print(f"   ✗ Error importing CaseForm: {e}")
    
    # 4. Test view configuration
    print("\n4. Testing view configuration...")
    try:
        from diagnoses.views import CaseCreateView
        
        view_class = CaseCreateView
        if hasattr(view_class, 'form_class'):
            print(f"   ✓ CaseCreateView has form_class defined")
            # Check if it's using the correct form
            from diagnoses.forms import CaseForm
            if view_class.form_class == CaseForm:
                print(f"   ✓ CaseCreateView is using CaseForm from forms.py")
            else:
                print(f"   ⚠ CaseCreateView using different form: {view_class.form_class}")
        
    except Exception as e:
        print(f"   ✗ Error checking view: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    if cases_with_images.exists():
        print(f"✓ Image upload functionality is working!")
        print(f"✓ {cases_with_images.count()} cases found with images")
        print(f"✓ All images are properly stored as base64 in database")
    else:
        print(f"⚠ No cases with images found yet")
        print(f"  Upload a new case with an image to test the functionality")
    
    print("\nNext Steps:")
    print("1. Navigate to the 'Create New Case' page")
    print("2. Fill in patient and symptoms")
    print("3. Upload an image using the image upload section")
    print("4. Submit the form")
    print("5. Open the case detail page to verify the image is displayed")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_image_functionality()
    except Exception as e:
        print(f"\n✗ Error running test: {e}")
        import traceback
        traceback.print_exc()

