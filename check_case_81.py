import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

c = Case.objects.get(id=81)
print(f"AI Diagnosis: {c.ai_diagnosis}")
print(f"\nAI Explanation: {c.ai_explanation[:300] if c.ai_explanation else 'None'}...")
print(f"\nImmediate Actions: {c.immediate_actions}")

# Check patient date of birth
print(f"\nPatient: {c.patient.first_name} {c.patient.last_name}")
print(f"Date of Birth: {c.patient.date_of_birth}")
print(f"Age: {c.patient.get_age() if c.patient.date_of_birth else 'N/A'}")
