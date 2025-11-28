"""
Test script to verify the comprehensive medication database is working correctly.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.medication_database import (
    get_medication_by_diagnosis,
    determine_severity_from_vitals,
    MEDICATION_DATABASE
)


def test_medication_database():
    """Test the medication database with various diagnoses."""
    
    print("=" * 80)
    print("TESTING COMPREHENSIVE MEDICATION DATABASE")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'diagnosis': 'Malaria',
            'severity': 'uncomplicated',
            'vital_signs': {'temperature': 38.5},
            'symptoms': 'fever, headache, body aches'
        },
        {
            'diagnosis': 'Pneumonia',
            'severity': 'severe',
            'vital_signs': {'temperature': 39.5, 'respiratory_rate': 35},
            'symptoms': 'difficulty breathing, high fever, chest pain'
        },
        {
            'diagnosis': 'Upper Respiratory Tract Infection',
            'severity': 'mild',
            'vital_signs': {'temperature': 37.5},
            'symptoms': 'runny nose, sore throat'
        },
        {
            'diagnosis': 'Typhoid Fever',
            'severity': 'moderate',
            'vital_signs': {'temperature': 39.0},
            'symptoms': 'fever, abdominal pain, headache'
        },
        {
            'diagnosis': 'Diarrhea',
            'severity': 'mild',
            'vital_signs': {},
            'symptoms': 'watery stools, mild dehydration'
        },
        {
            'diagnosis': 'Snake Bite',
            'severity': 'emergency',
            'vital_signs': {},
            'symptoms': 'snake bite, swelling, bleeding'
        },
        {
            'diagnosis': 'Hypertension',
            'severity': 'moderate',
            'vital_signs': {},
            'symptoms': 'high blood pressure'
        },
        {
            'diagnosis': 'Diabetes Mellitus Type 2',
            'severity': 'mild',
            'vital_signs': {},
            'symptoms': 'high blood sugar'
        },
        {
            'diagnosis': 'Urinary Tract Infection',
            'severity': 'uncomplicated',
            'vital_signs': {},
            'symptoms': 'burning urination, frequency'
        }
    ]
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {idx}: {test_case['diagnosis']} ({test_case['severity']})")
        print('=' * 80)
        
        # Get medications
        result = get_medication_by_diagnosis(
            test_case['diagnosis'],
            severity=test_case['severity']
        )
        
        # Display primary medications
        print("\n📋 PRIMARY MEDICATIONS:")
        for med in result.get('primary_medications', []):
            print(f"\n  ✓ {med.get('name', 'Unknown')}")
            print(f"    Dosage: {med.get('dosage', 'N/A')}")
            print(f"    Duration: {med.get('duration', 'N/A')}")
            print(f"    Instructions: {med.get('instructions', 'N/A')[:100]}...")
            if med.get('contraindications'):
                print(f"    ⚠️  Contraindications: {med.get('contraindications')}")
            if med.get('source'):
                print(f"    📚 Source: {med.get('source')}")
        
        # Display supportive care
        if result.get('supportive_care'):
            print("\n🏥 SUPPORTIVE CARE:")
            for care in result.get('supportive_care', [])[:3]:
                print(f"  • {care}")
        
        # Display lifestyle recommendations
        if result.get('lifestyle'):
            print("\n💪 LIFESTYLE RECOMMENDATIONS:")
            for lifestyle in result.get('lifestyle', [])[:3]:
                print(f"  • {lifestyle}")
        
        # Display prevention
        if result.get('prevention'):
            print("\n🛡️  PREVENTION:")
            for prev in result.get('prevention', [])[:3]:
                print(f"  • {prev}")
    
    # Test severity determination
    print(f"\n{'=' * 80}")
    print("TESTING SEVERITY DETERMINATION")
    print('=' * 80)
    
    severity_tests = [
        {'temperature': 37.5, 'respiratory_rate': 18, 'symptoms': 'mild cough', 'expected': 'mild'},
        {'temperature': 38.5, 'respiratory_rate': 22, 'symptoms': 'fever headache', 'expected': 'moderate'},
        {'temperature': 39.5, 'respiratory_rate': 35, 'symptoms': 'difficulty breathing', 'expected': 'severe'},
        {'temperature': 40.0, 'respiratory_rate': 30, 'symptoms': 'unconscious', 'expected': 'severe'},
    ]
    
    for test in severity_tests:
        vital_signs = {
            'temperature': test['temperature'],
            'respiratory_rate': test['respiratory_rate']
        }
        severity = determine_severity_from_vitals(vital_signs, test['symptoms'])
        status = "✓" if severity == test['expected'] else "✗"
        print(f"\n{status} Temp: {test['temperature']}°C, RR: {test['respiratory_rate']}, "
              f"Symptoms: '{test['symptoms']}' → Severity: {severity} (expected: {test['expected']})")
    
    # Test database coverage
    print(f"\n{'=' * 80}")
    print("DATABASE COVERAGE")
    print('=' * 80)
    print(f"\nTotal diagnoses in database: {len(MEDICATION_DATABASE)}")
    print("\nAvailable diagnoses:")
    for diagnosis in MEDICATION_DATABASE.keys():
        print(f"  ✓ {diagnosis}")
    
    print("\n" + "=" * 80)
    print("✅ MEDICATION DATABASE TESTING COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_medication_database()
