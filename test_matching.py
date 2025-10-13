import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine

engine = MedicalAIDiagnosticEngine()
symptoms = 'High fever, severe headache, body aches, fatigue, chills'
patient_history = {'age': 8, 'gender': 'Male'}

# Test _match_condition_rules directly
print("Testing _match_condition_rules...")
matches = engine._match_condition_rules(symptoms, patient_history)
print(f"Matches found: {len(matches)}")
for m in matches:
    print(f"  - {m['condition']}: {m['confidence']:.2f} (urgency: {m['urgency']})")
