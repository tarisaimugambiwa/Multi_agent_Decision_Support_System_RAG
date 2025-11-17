#!/usr/bin/env python
"""
Test script to verify the image upload fix works correctly.
Tests the form field configuration and clean_symptom_image method.
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
    img = Image.new('RGB', (200, 200), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=85)
    img_io.seek(0)
    img_io.name = 'test_symptom.jpg'
    return img_io

def test_form_has_symptom_image():
    """Test that symptom_image_file field is in CaseForm."""
    print("TEST 1: Verify symptom_image_file field in CaseForm")
    print("-" * 50)
    
    form = CaseForm()
    form_fields = list(form.fields.keys())
    print(f"Form fields: {form_fields}")
    
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
        test_img = create_test_image()
        
        # Create form but don't validate yet
        form = CaseForm()
        
        # Manually invoke the clean method to test it directly
        form.cleaned_data = {}
        form.cleaned_data['symptom_image_file'] = test_img
        
        # Call the clean method
        result = form.clean_symptom_image_file()
        
        if hasattr(form, 'base64_image_data'):
            print("✓ PASS: base64_image_data attribute created")
            print(f"  - Base64 data length: {len(form.base64_image_data)} chars")
            print(f"  - Filename: {form.base64_image_filename}")
            print(f"  - Data starts with: {form.base64_image_data[:20]}...")
            return True
        else:
            print("✗ FAIL: base64_image_data attribute not found")
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
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
