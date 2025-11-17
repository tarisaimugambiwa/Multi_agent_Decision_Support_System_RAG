import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

# Get the 5 most recent cases
cases = Case.objects.all().order_by('-id')[:5]

print("\nRecent cases:")
print("="*70)
for c in cases:
    img_size = len(c.symptom_image) if c.symptom_image else 0
    print(f"Case #{c.id}:")
    print(f"  Patient: {c.patient}")
    print(f"  Symptoms: {c.symptoms[:50]}...")
    print(f"  Image: {img_size} chars")
    print(f"  Filename: {c.symptom_image_filename}")
    print(f"  Created: {c.created_at}")
    print("-"*70)
