import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine

# Create engine and test matching
engine = MedicalAIDiagnosticEngine()
symptoms = 'High fever, severe headache, body aches, fatigue, chills'
patient_history = {'age': 8, 'gender': 'Male'}

print("Testing symptom matching...")
print(f"Symptoms: {symptoms}")
print(f"Confidence threshold: {engine.confidence_threshold}")
print()

# Check each condition manually
symptoms_lower = symptoms.lower()
print("Checking conditions...")
for condition, rules in engine.condition_rules.items():
    print(f"\n{condition}:")
    print(f"  Required: {rules['required_symptoms']}")
    
    # Check required
    required_count = 0
    for symptom in rules['required_symptoms']:
        symptom_words = symptom.split()
        matches = any(word in symptoms_lower for word in symptom_words)
        if matches:
            required_count += 1
            print(f"    ✓ '{symptom}' found")
        else:
            print(f"    ✗ '{symptom}' not found")
    
    if required_count > 0:
        print(f"  -> Would continue with confidence calculation")
    else:
        print(f"  -> Skipped (no required symptoms)")

# Now run actual diagnosis
print("\n" + "="*60)
print("Running actual diagnosis...")
result = engine.get_ai_diagnosis(symptoms, patient_history)
print(f"Primary diagnoses: {len(result.get('primary_diagnoses', []))}")
for dx in result.get('primary_diagnoses', []):
    print(f"  - {dx['condition']}: {dx['confidence']:.2f}")
