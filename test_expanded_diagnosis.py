#!/usr/bin/env python
"""
Test the expanded diagnosis system with various conditions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine

# Initialize the diagnostic engine
engine = MedicalAIDiagnosticEngine()

# Test cases covering different conditions
test_cases = [
    {
        'name': 'Malaria Case',
        'symptoms': 'High fever for 2 days, severe chills, sweating, body aches, headache, nausea',
        'patient_history': {
            'age': 8,
            'gender': 'Female',
            'medical_history': 'Lives in malaria-endemic area'
        }
    },
    {
        'name': 'Pneumonia Case',
        'symptoms': 'Persistent cough with yellow sputum, high fever, chest pain, difficulty breathing, fatigue',
        'patient_history': {
            'age': 65,
            'gender': 'Male',
            'medical_history': 'Chronic smoker, diabetes'
        }
    },
    {
        'name': 'Gastroenteritis Case',
        'symptoms': 'Severe diarrhea for 3 days, vomiting, abdominal cramps, dehydration, fever',
        'patient_history': {
            'age': 5,
            'gender': 'Male',
            'medical_history': 'Recent travel, drank untreated water'
        }
    },
    {
        'name': 'Diabetes/DKA Case',
        'symptoms': 'Excessive thirst, frequent urination, nausea, vomiting, abdominal pain, confusion',
        'patient_history': {
            'age': 35,
            'gender': 'Female',
            'medical_history': 'Family history of diabetes, recent infection'
        }
    },
    {
        'name': 'Meningitis Case',
        'symptoms': 'Severe headache, high fever, stiff neck, sensitivity to light, confusion, nausea',
        'patient_history': {
            'age': 20,
            'gender': 'Male',
            'medical_history': 'Recent upper respiratory infection'
        }
    },
    {
        'name': 'TB Case',
        'symptoms': 'Persistent cough for 3 weeks, night sweats, weight loss, fever, chest pain, blood in sputum',
        'patient_history': {
            'age': 40,
            'gender': 'Male',
            'medical_history': 'HIV positive, contact with TB patient'
        }
    },
    {
        'name': 'UTI Case',
        'symptoms': 'Frequent urination, burning sensation when urinating, cloudy urine, pelvic pain, fever',
        'patient_history': {
            'age': 28,
            'gender': 'Female',
            'medical_history': 'Sexually active'
        }
    },
    {
        'name': 'Migraine Case',
        'symptoms': 'Severe throbbing headache on one side, nausea, sensitivity to light and sound, visual disturbances',
        'patient_history': {
            'age': 32,
            'gender': 'Female',
            'medical_history': 'Family history of migraines, stress at work'
        }
    }
]

print("=" * 100)
print("TESTING EXPANDED DIAGNOSIS SYSTEM")
print("=" * 100)
print(f"\nTotal Conditions in System: {len(engine.condition_rules)}")
print("\nConditions available:")
for i, condition in enumerate(sorted(engine.condition_rules.keys()), 1):
    print(f"  {i}. {condition.replace('_', ' ').title()}")

print("\n" + "=" * 100)
print("RUNNING DIAGNOSTIC TESTS")
print("=" * 100)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'='*100}")
    print(f"TEST CASE {i}: {test_case['name']}")
    print(f"{'='*100}")
    print(f"Symptoms: {test_case['symptoms']}")
    print(f"Patient: {test_case['patient_history']['age']}yo {test_case['patient_history']['gender']}")
    print(f"History: {test_case['patient_history']['medical_history']}")
    print("-" * 100)
    
    # Run diagnosis
    result = engine.get_ai_diagnosis(
        symptoms=test_case['symptoms'],
        patient_history=test_case['patient_history']
    )
    
    # Display results
    print("\n🔍 DIAGNOSTIC RESULTS:")
    print(f"  Urgency Level: {result['urgency_level'].upper()}")
    print(f"  Severity Score: {result['severity_score']}")
    print(f"  Knowledge Sources Consulted: {result['knowledge_sources']}")
    
    if result['primary_diagnoses']:
        print(f"\n  📊 PRIMARY DIAGNOSES ({len(result['primary_diagnoses'])}):")
        for j, diagnosis in enumerate(result['primary_diagnoses'], 1):
            print(f"    {j}. {diagnosis['condition']}")
            print(f"       Confidence: {diagnosis['confidence']*100:.1f}%")
            print(f"       Reasoning: {diagnosis.get('reasoning', 'Pattern-based matching')}")
    else:
        print("\n  ⚠️ No specific diagnosis matched")
    
    if result.get('ai_diagnosis'):
        print(f"\n  🤖 AI DIAGNOSIS (Ollama):")
        print(f"     {result['ai_diagnosis']}")
        if result.get('ai_reasoning'):
            print(f"     Reasoning: {result['ai_reasoning']}")
    
    if result['treatment_recommendations']:
        print(f"\n  💊 TREATMENT RECOMMENDATIONS:")
        for j, treatment in enumerate(result['treatment_recommendations'][:2], 1):
            print(f"    {j}. {treatment[:150]}...")
    
    print("\n" + "-" * 100)

print("\n" + "=" * 100)
print("TEST COMPLETE")
print("=" * 100)
