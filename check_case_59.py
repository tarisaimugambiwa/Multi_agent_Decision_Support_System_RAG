import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

# Check case #59
try:
    case = Case.objects.get(id=59)
    print(f"\nCase #59:")
    print(f"  Patient: {case.patient}")
    print(f"  Symptoms: {case.symptoms}")
    print(f"  Image: {len(case.symptom_image) if case.symptom_image else 0} chars")
    print(f"  Filename: {case.symptom_image_filename}")
    print(f"  Created: {case.created_at}")
    
    if case.symptom_image:
        print(f"\n✅ IMAGE SAVED SUCCESSFULLY!")
        print(f"View at: http://127.0.0.1:8000/diagnoses/59/")
    else:
        print(f"\n❌ NO IMAGE DATA")
except Case.DoesNotExist:
    print("Case #59 does not exist")
