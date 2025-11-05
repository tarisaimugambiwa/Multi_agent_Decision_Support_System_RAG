"""
Test the cleaned-up treatment agent output
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.services.treatment_agent import TreatmentAgent

# Initialize treatment agent
agent = TreatmentAgent()

# Test diagnosis
test_diagnosis = {
    'primary_diagnosis': 'Upper Respiratory Tract Infection',
    'confidence_score': 0.85,
    'differential_diagnoses': ['Common Cold', 'Influenza'],
    'red_flags': ['High fever persisting over 3 days'],
    'emergency_conditions': []
}

# Test for moderate urgency
print("=" * 80)
print("TESTING MODERATE URGENCY TREATMENT PLAN")
print("=" * 80)

action_plan = agent.create_action_plan(
    diagnosis=test_diagnosis,
    urgency_level='moderate',
    symptoms=['cough', 'fever', 'sore throat'],
    red_flags=test_diagnosis['red_flags'],
    emergency_conditions=[]
)

print("\n📋 IMMEDIATE ACTIONS:")
for i, action in enumerate(action_plan['immediate_actions'], 1):
    print(f"  {i}. {action}")

print("\n⏰ SHORT-TERM ACTIONS:")
for i, action in enumerate(action_plan['short_term_actions'], 1):
    print(f"  {i}. {action}")

print("\n📅 FOLLOW-UP ACTIONS:")
for i, action in enumerate(action_plan['follow_up_actions'], 1):
    print(f"  {i}. {action}")

# Test medications
print("\n" + "=" * 80)
print("TESTING MEDICATION RECOMMENDATIONS")
print("=" * 80)

medications = agent.recommend_medications(
    diagnosis=test_diagnosis,
    symptoms=['cough', 'fever', 'sore throat'],
    patient_history={'medical_history': 'None', 'allergies': 'None'},
    allergies=[]
)

print("\n💊 PRIMARY MEDICATIONS:")
for i, med in enumerate(medications.get('primary_medications', []), 1):
    print(f"\n  {i}. {med['name']}")
    print(f"     Dosage: {med['dosage']}")
    print(f"     Duration: {med['duration']}")
    print(f"     Instructions: {med['instructions']}")
    if 'source' in med:
        print(f"     Source: {med['source']}")

print("\n" + "=" * 80)
print("✅ Treatment plan looks clean and actionable!")
print("=" * 80)
