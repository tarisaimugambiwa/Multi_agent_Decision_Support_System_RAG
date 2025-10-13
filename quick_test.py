import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import get_ai_diagnosis

# Test with fever symptoms
result = get_ai_diagnosis(
    'High fever, severe headache, body aches, fatigue, chills',
    {'age': 8, 'gender': 'Male'}
)

dx_list = result.get('primary_diagnoses', [])
print(f"Found {len(dx_list)} diagnoses")
for d in dx_list[:3]:
    print(f"  - {d['condition']}: Confidence {d['confidence']:.2f}, Urgency: {d['urgency']}")

print(f"\nUrgency Level: {result.get('urgency_level')}")
print(f"Knowledge Sources: {result.get('knowledge_sources')}")
