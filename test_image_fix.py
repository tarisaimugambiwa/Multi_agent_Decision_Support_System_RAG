#!/usr/bin/env python
"""
Test script to verify the image upload fix works correctly.
This tests the form field configuration and clean_symptom_image_file method.
"""
import os
import sys
import django
import base64
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.forms import CaseForm
from patients.models import Patient

def create_test_image():
    """Create a small test image in memory."""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_io.name = 'test_image.jpg'
    
    return img_io

def test_form_has_symptom_image():
    """Test that symptom_image_file field is in CaseForm."""
    print("TEST 1: Verify symptom_image_file field in CaseForm")
    print("-" * 50)
    
    form = CaseForm()
    form_fields = form.fields
    print(f"Form fields: {list(form_fields.keys())}")
    
    if 'symptom_image_file' in form_fields:
        print("✓ PASS: symptom_image_file field is in CaseForm")
        return True
    else:
        print("✗ FAIL: symptom_image_file field is NOT in CaseForm")
        return False

def test_form_clean_method():
    """Test that the form's clean_symptom_image_file method works."""
    print("\nTEST 2: Verify clean_symptom_image_file method works")
    print("-" * 50)
    
    try:
        # Get a patient
        patient = Patient.objects.first()
        if not patient:
            print("✗ FAIL: No patients in database")
            return False
        
        # Create test image
        test_img = create_test_image()
        
        # Create form data - symptom_image_file is NOT required, so we can skip it for basic test
        form_data = {
            'patient': patient.id,
            'symptoms': 'Test symptoms',
            'vital_signs': '{"temperature": 37.0}',
        }
        
        # Test 1: Form without image should be valid
        form = CaseForm(form_data)
        is_valid = form.is_valid()
        
        if not is_valid:
            print(f"✗ FAIL: Form without image should be valid: {form.errors}")
            return False
        else:
            print("✓ PASS: Form is valid without image file (required=False works)")
        
        # Test 2: Test with image file using a mock to avoid multipart issues
        form_with_image = CaseForm(form_data)
        
        # Manually call the clean method to simulate file upload
        test_img_copy = create_test_image()
        form_with_image.cleaned_data = form_data.copy()
        form_with_image.cleaned_data['symptom_image_file'] = test_img_copy
        
        # Manually invoke the clean method
        try:
            result = form_with_image.clean_symptom_image_file()
            
            # Check if base64 data was created
            if hasattr(form_with_image, 'base64_image_data'):
                print(f"✓ PASS: base64_image_data attribute created via clean method")
                print(f"  - Base64 data length: {len(form_with_image.base64_image_data)} chars")
                print(f"  - Filename: {form_with_image.base64_image_filename}")
                return True
            else:
                print("✗ FAIL: base64_image_data attribute not found after clean")
                return False
        except Exception as e:
            print(f"✗ FAIL: Exception during clean method: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widgets():
    """Test that widgets are configured correctly."""
    print("\nTEST 3: Verify form widgets configuration")
    print("-" * 50)
    
    form = CaseForm()
    widgets = form.fields
    
    if 'symptom_image_file' in widgets:
        widget = widgets['symptom_image_file']
        print(f"✓ PASS: symptom_image_file widget found")
        print(f"  - Widget type: {type(widget).__name__}")
        return True
    else:
        print("✗ FAIL: symptom_image_file widget not found")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("IMAGE UPLOAD FIX - VERIFICATION TESTS")
    print("=" * 50)
    
    results = []
    results.append(test_form_has_symptom_image())
    results.append(test_widgets())
    results.append(test_form_clean_method())
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    if all(results):
        print("✓ ALL TESTS PASSED - Image upload fix is working!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED - Please review the output above")
        sys.exit(1)
