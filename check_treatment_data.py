"""
Quick script to check treatment data structure in existing cases
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.models import Case

# Get the most recent case
case = Case.objects.order_by('-created_at').first()

if case:
    print(f"\n=== Case #{case.id} ===")
    print(f"Patient: {case.patient.full_name}")
    print(f"Status: {case.status}")
    print(f"Priority: {case.priority}")
    
    if case.ai_diagnosis:
        ai_data = json.loads(case.ai_diagnosis)
        
        print(f"\n=== Diagnosis ===")
        print(f"Primary: {ai_data.get('diagnosis', {}).get('primary_diagnosis', 'N/A')}")
        print(f"Confidence: {ai_data.get('diagnosis', {}).get('confidence', 'N/A')}")
        
        print(f"\n=== Treatment Structure ===")
        treatment = ai_data.get('treatment')
        if treatment:
            print(f"Treatment type: {type(treatment)}")
            print(f"Treatment keys: {treatment.keys() if isinstance(treatment, dict) else 'Not a dict'}")
            
            # Check medications structure
            if 'medications' in treatment:
                meds = treatment['medications']
                print(f"\nMedications type: {type(meds)}")
                print(f"Medications keys: {meds.keys() if isinstance(meds, dict) else 'Not a dict'}")
                
                if isinstance(meds, dict):
                    if 'primary_medications' in meds:
                        print(f"\nPrimary medications: {len(meds['primary_medications'])} items")
                        if meds['primary_medications']:
                            print(f"First med structure: {meds['primary_medications'][0]}")
                    else:
                        print("\n⚠️ No 'primary_medications' key found")
                        print(f"Available keys: {list(meds.keys())}")
            else:
                print("\n⚠️ No 'medications' key in treatment")
                
            # Check immediate actions
            if 'immediate_actions' in treatment:
                print(f"\nImmediate actions: {len(treatment['immediate_actions'])} items")
            else:
                print("\n⚠️ No 'immediate_actions' key in treatment")
        else:
            print("⚠️ Treatment is None or missing")
    else:
        print("\n⚠️ No AI diagnosis data found")
else:
    print("No cases found in database")
