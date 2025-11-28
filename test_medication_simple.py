"""
Simple test of medication database without Django dependencies.
"""

import sys
sys.path.insert(0, r'c:\Users\tarisaim\Desktop\DS_System')

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
        ('Malaria', 'uncomplicated'),
        ('Pneumonia', 'severe'),
        ('Upper Respiratory Tract Infection', 'mild'),
        ('Typhoid Fever', 'moderate'),
        ('Diarrhea', 'mild'),
        ('Snake Bite', 'emergency'),
        ('Hypertension', 'moderate'),
        ('Diabetes Mellitus Type 2', 'mild'),
        ('Urinary Tract Infection', 'uncomplicated'),
    ]
    
    for idx, (diagnosis, severity) in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {idx}: {diagnosis} ({severity})")
        print('=' * 80)
        
        # Get medications
        result = get_medication_by_diagnosis(diagnosis, severity=severity)
        
        # Display primary medications
        print("\n📋 PRIMARY MEDICATIONS:")
        meds = result.get('primary_medications', [])
        if isinstance(meds, list) and len(meds) > 0:
            for med in meds[:2]:  # Show first 2
                if isinstance(med, dict):
                    print(f"\n  ✓ {med.get('name', 'Unknown')}")
                    print(f"    Dosage: {med.get('dosage', 'N/A')[:80]}...")
                    print(f"    Duration: {med.get('duration', 'N/A')}")
                    if med.get('source'):
                        print(f"    📚 Source: {med.get('source')}")
        else:
            print("  No medications found")
        
        # Display supportive care
        supportive = result.get('supportive_care', [])
        if supportive:
            print(f"\n🏥 SUPPORTIVE CARE ({len(supportive)} items):")
            for care in supportive[:2]:
                print(f"  • {care[:60]}...")
        
        # Display lifestyle recommendations
        lifestyle = result.get('lifestyle', [])
        if lifestyle:
            print(f"\n💪 LIFESTYLE ({len(lifestyle)} items):")
            for item in lifestyle[:2]:
                print(f"  • {item[:60]}...")
    
    # Test severity determination
    print(f"\n{'=' * 80}")
    print("TESTING SEVERITY DETERMINATION")
    print('=' * 80)
    
    severity_tests = [
        ({'temperature': 37.5, 'respiratory_rate': 18}, 'mild cough', 'mild'),
        ({'temperature': 38.5, 'respiratory_rate': 22}, 'fever headache', 'moderate'),
        ({'temperature': 39.5, 'respiratory_rate': 35}, 'difficulty breathing', 'severe'),
        ({'temperature': 40.0}, 'unconscious', 'severe'),
    ]
    
    for vital_signs, symptoms, expected in severity_tests:
        severity = determine_severity_from_vitals(vital_signs, symptoms)
        status = "✓" if severity == expected else "✗"
        temp = vital_signs.get('temperature', 'N/A')
        print(f"{status} Temp: {temp}°C, Symptoms: '{symptoms}' → {severity} (expected: {expected})")
    
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
