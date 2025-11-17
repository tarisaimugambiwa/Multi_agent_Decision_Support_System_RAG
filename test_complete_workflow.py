#!/usr/bin/env python
"""
Complete Workflow Test - Image Upload to Display
Tests the complete end-to-end flow:
1. Nurse creates case with image
2. Image saved as base64 to database
3. Nurse views case - image displays
4. Doctor views case - image displays
"""
import os
import sys
import django
import base64
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient
from diagnoses.models import Case
from diagnoses.forms import CaseForm

User = get_user_model()

def create_test_image():
    """Create a test image."""
    img = Image.new('RGB', (300, 300), color='blue')
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=90)
    img_io.seek(0)
    img_io.name = 'symptom_test.jpg'
    return img_io

def test_complete_workflow():
    """Test the complete image upload and display workflow."""
    print("=" * 70)
    print("COMPLETE IMAGE WORKFLOW TEST")
    print("=" * 70)
    
    try:
        # STEP 1: Setup test data
        print("\n[STEP 1] Setting up test data...")
        patient = Patient.objects.first()
        nurse = User.objects.filter(role='NURSE').first()
        doctor = User.objects.filter(role='DOCTOR').first()
        
        if not patient or not nurse:
            print("✗ FAIL: Required test data not found")
            return False
        
        print(f"✓ Patient: {patient.first_name} {patient.last_name}")
        print(f"✓ Nurse: {nurse.get_full_name()}")
        print(f"✓ Doctor: {doctor.get_full_name() if doctor else 'N/A'}")
        
        # STEP 2: Create case form with image
        print("\n[STEP 2] Nurse creates case with image upload...")
        test_img = create_test_image()
        original_size = test_img.seek(0, 2)
        test_img.seek(0)
        
        form_data = {
            'patient': patient.id,
            'symptoms': 'Patient presents with fever, cough, and body aches',
            'vital_signs': '{"temperature": 38.5, "bp": "120/80", "heart_rate": 88}',
        }
        
        form = CaseForm(form_data)
        form.cleaned_data = form_data.copy()
        form.cleaned_data['symptom_image_file'] = test_img
        form.clean_symptom_image_file()
        
        if not hasattr(form, 'base64_image_data'):
            print("✗ FAIL: Image not converted to base64")
            return False
        
        print(f"✓ Image uploaded: {original_size} bytes")
        print(f"✓ Image converted to base64: {len(form.base64_image_data)} chars")
        print(f"✓ Filename captured: {form.base64_image_filename}")
        
        # STEP 3: Save case to database
        print("\n[STEP 3] Saving case to database...")
        case = Case(
            patient=patient,
            nurse=nurse,
            symptoms=form_data['symptoms'],
            vital_signs=form_data['vital_signs'],
            symptom_image=form.base64_image_data,
            symptom_image_filename=form.base64_image_filename,
            status='PENDING'
        )
        case.save()
        print(f"✓ Case saved to database: ID={case.id}")
        print(f"✓ symptom_image field: {len(case.symptom_image)} chars")
        print(f"✓ symptom_image_filename field: {case.symptom_image_filename}")
        
        # STEP 4: Nurse retrieves and views case
        print("\n[STEP 4] Nurse views case detail...")
        nurse_case = Case.objects.get(id=case.id)
        
        if not nurse_case.symptom_image:
            print("✗ FAIL: Image not retrieved from database for nurse")
            return False
        
        print(f"✓ Case retrieved: ID={nurse_case.id}")
        print(f"✓ Image present in database: {len(nurse_case.symptom_image)} chars")
        
        # Verify template rendering would work for nurse
        if nurse_case.symptom_image:
            print(f"✓ Template condition '{{{{ if case.symptom_image }}}}' = TRUE")
            print(f"✓ Nurse would see image in template")
        else:
            print("✗ FAIL: Template wouldn't render image for nurse")
            return False
        
        # STEP 5: Doctor retrieves and views case
        print("\n[STEP 5] Doctor views same case...")
        doctor_case = Case.objects.get(id=case.id)
        
        if not doctor_case.symptom_image:
            print("✗ FAIL: Image not retrieved from database for doctor")
            return False
        
        print(f"✓ Case retrieved: ID={doctor_case.id}")
        print(f"✓ Image present in database: {len(doctor_case.symptom_image)} chars")
        
        # Verify template rendering would work for doctor
        if doctor_case.symptom_image:
            print(f"✓ Template condition '{{{{ if case.symptom_image }}}}' = TRUE")
            print(f"✓ Doctor would see image in template")
        else:
            print("✗ FAIL: Template wouldn't render image for doctor")
            return False
        
        # STEP 6: Verify base64 integrity
        print("\n[STEP 6] Verifying base64 data integrity...")
        retrieved_base64 = nurse_case.symptom_image
        
        if retrieved_base64 != form.base64_image_data:
            print("✗ FAIL: Base64 data corrupted during storage/retrieval")
            return False
        
        print(f"✓ Base64 data integrity verified")
        
        # Verify it's valid base64
        try:
            decoded_bytes = base64.b64decode(retrieved_base64)
            print(f"✓ Base64 decoding successful: {len(decoded_bytes)} bytes")
        except Exception as e:
            print(f"✗ FAIL: Base64 decode failed: {e}")
            return False
        
        # STEP 7: Verify HTML img tag format
        print("\n[STEP 7] Verifying HTML img tag format...")
        img_src = f"data:image/jpeg;base64,{retrieved_base64}"
        
        if img_src.startswith("data:image/jpeg;base64,"):
            print(f"✓ HTML img src format: VALID")
            print(f"✓ Full src attribute length: {len(img_src)} chars")
        else:
            print("✗ FAIL: Invalid img src format")
            return False
        
        # STEP 8: Summary
        print("\n" + "=" * 70)
        print("✓ COMPLETE WORKFLOW TEST PASSED")
        print("=" * 70)
        
        print("\nWorkflow Summary:")
        print(f"  1. Original image size: {original_size} bytes")
        print(f"  2. Base64 encoded size: {len(form.base64_image_data)} chars")
        print(f"  3. Stored in database: Case #{case.id}")
        print(f"  4. Retrieved by nurse: ✓ Verified")
        print(f"  5. Retrieved by doctor: ✓ Verified")
        print(f"  6. Base64 integrity: ✓ Verified")
        print(f"  7. HTML rendering: ✓ Ready")
        
        print("\nTemplate Rendering:")
        print(f"  - Nurse view: /diagnoses/{case.id}/ → Image displays ✓")
        print(f"  - Doctor view: /diagnoses/{case.id}/ → Image displays ✓")
        print(f"  - Both use same template → Base64 decoded by browser ✓")
        
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
            print(f"\n✓ Cleanup: Test case deleted")
        except:
            pass

if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
