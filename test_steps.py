import os, django, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine
from knowledge.rag_utils import search_medical_knowledge, get_treatment_recommendations

engine = MedicalAIDiagnosticEngine()
symptoms = 'High fever, severe headache, body aches, fatigue, chills'
patient_history = {'age': 8, 'gender': 'Male'}

print("Step 1: Test search_medical_knowledge...")
try:
    results = search_medical_knowledge(symptoms, top_k=5)
    print(f"  OK - Got {len(results)} results")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

print("\nStep 2: Test _match_condition_rules...")
try:
    matches = engine._match_condition_rules(symptoms, patient_history)
    print(f"  OK - Got {len(matches)} matches")
    if matches:
        print(f"  Top: {matches[0]['condition']}")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

print("\nStep 3: Test get_treatment_recommendations...")
try:
    if matches:
        treatment = get_treatment_recommendations(matches[0]['condition'], top_k=3)
        print(f"  OK - Got {len(treatment)} treatment recs")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

print("\nStep 4: Test get_ai_diagnosis...")
try:
    result = engine.get_ai_diagnosis(symptoms, patient_history)
    print(f"  OK - primary_diagnoses: {len(result.get('primary_diagnoses', []))}")
    print(f"  Result keys: {list(result.keys())}")
    if 'error' in result:
        print(f"  ERROR IN RESULT: {result['error']}")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()
