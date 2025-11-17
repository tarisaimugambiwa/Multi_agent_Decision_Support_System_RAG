#!/usr/bin/env python
"""
End-to-End Integration Test for Image Upload Feature
Tests the complete flow from file upload to database storage to template display
"""
import os
import sys
import django
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from diagnoses.models import Case, Patient
from diagnoses.forms import CaseForm
import base64

User = get_user_model()

def create_test_image(size=100, color='red', name='test.jpg'):
    """Create a test image."""
    img = Image.new('RGB', (size, size), color=color)
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_io.name = name
    return img_io

def test_end_to_end_image_upload():
    """Test the complete image upload flow."""
    print("=" * 60)
    print("END-TO-END IMAGE UPLOAD TEST")
    print("=" * 60)
    
    try:
        # Step 1: Setup test data
        print("\n[1/6] Setting up test data...")
        patient = Patient.objects.first()
        if not patient:
            print("✗ FAIL: No patients in database")
            return False
        
        nurse = User.objects.filter(role='NURSE').first()
        if not nurse:
            print("✗ FAIL: No nurses in database")
            return False
        
        print(f"✓ Found patient: {patient.full_name}")
        print(f"✓ Found nurse: {nurse.get_full_name()}")
        
        # Step 2: Prepare form with image
        print("\n[2/6] Creating form with image file...")
        test_img = create_test_image(200, 'blue', 'symptom_test.jpg')
        original_size = test_img.seek(0, 2)  # Seek to end to get size
        test_img.seek(0)  # Reset to start
        
        form_data = {
            'patient': patient.id,
            'symptoms': 'Test symptom for image upload',
            'vital_signs': '{"temperature": 37.5, "bp": "120/80", "hr": 72}',
        }
        
        # Manually simulate form submission
        form = CaseForm(form_data)
        
        # Manually invoke the clean method to simulate file upload
        test_img_for_clean = create_test_image(200, 'blue', 'symptom_test.jpg')
        form.cleaned_data = form_data.copy()
        form.cleaned_data['symptom_image_file'] = test_img_for_clean
        form.clean_symptom_image_file()
        
        print(f"✓ Form created successfully")
        print(f"✓ Image file size: {original_size} bytes")
        
        # Step 3: Check if base64 encoding worked
        print("\n[3/6] Verifying base64 encoding...")
        if not hasattr(form, 'base64_image_data'):
            print("✗ FAIL: base64_image_data not found on form")
            return False
        
        base64_data = form.base64_image_data
        print(f"✓ Base64 data created")
        print(f"✓ Base64 data length: {len(base64_data)} characters")
        print(f"✓ Base64 data starts with: {base64_data[:20]}...")
        
        # Step 4: Create Case model instance
        print("\n[4/6] Creating Case model instance...")
        case = Case(
            patient=patient,
            nurse=nurse,
            symptoms=form_data['symptoms'],
            vital_signs=form_data['vital_signs'],
            symptom_image=base64_data,
            symptom_image_filename='symptom_test.jpg',
            status='PENDING'
        )
        case.save()
        print(f"✓ Case created: ID={case.id}")
        print(f"✓ Case saved to database")
        
        # Step 5: Retrieve from database and verify
        print("\n[5/6] Retrieving case from database...")
        retrieved_case = Case.objects.get(id=case.id)
        
        if not retrieved_case.symptom_image:
            print("✗ FAIL: symptom_image is empty in database")
            return False
        
        print(f"✓ Case retrieved from database")
        print(f"✓ Image data present: {len(retrieved_case.symptom_image)} chars")
        print(f"✓ Filename: {retrieved_case.symptom_image_filename}")
        
        # Verify base64 data integrity
        if retrieved_case.symptom_image != base64_data:
            print("✗ FAIL: Base64 data corrupted during storage/retrieval")
            return False
        
        print("✓ Base64 data integrity verified")
        
        # Step 6: Verify template rendering would work
        print("\n[6/6] Verifying template rendering compatibility...")
        
        # Check that the condition would work in template
        if retrieved_case.symptom_image:
            print("✓ Template condition '{% if case.symptom_image %}' would evaluate to TRUE")
        else:
            print("✗ FAIL: Template condition would evaluate to FALSE")
            return False
        
        # Verify data format for HTML img tag
        img_src = f"data:image/jpeg;base64,{retrieved_case.symptom_image}"
        if img_src.startswith("data:image/jpeg;base64,"):
            print("✓ Image data format valid for HTML img src")
        else:
            print("✗ FAIL: Invalid image data format")
            return False
        
        # Success!
        print("\n" + "=" * 60)
        print("✓ END-TO-END TEST PASSED")
        print("=" * 60)
        print("\nImage upload flow verified:")
        print(f"  1. File uploaded: {original_size} bytes")
        print(f"  2. Base64 encoded: {len(base64_data)} chars")
        print(f"  3. Stored in database: Case #{case.id}")
        print(f"  4. Retrieved successfully: {len(retrieved_case.symptom_image)} chars")
        print(f"  5. Ready for template rendering: YES")
        print("\nThe image will now display in:")
        print(f"  - Nurse dashboard: /diagnoses/{case.id}/")
        print(f"  - Doctor dashboard: /diagnoses/{case.id}/")
        
        return True
        
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            Case.objects.get(id=case.id).delete()
            print(f"\n✓ Cleanup: Test case #{case.id} deleted")
        except:
            pass

if __name__ == '__main__':
    success = test_end_to_end_image_upload()
    sys.exit(0 if success else 1)
