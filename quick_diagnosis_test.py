#!/usr/bin/env python
"""
Quick single diagnosis test - Malaria case
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine

engine = MedicalAIDiagnosticEngine()

patient = {
    'patient_id': 'MALARIA_TEST',
    'age': 3,
    'gender': 'Female',
    'medical_history': 'Lives in malaria-endemic area',
    'vital_signs': {
        'temperature': '39.8°C',
        'heart_rate': '130/min',
        'respiratory_rate': '32/min'
    }
}

symptoms = "High fever for 2 days, severe headache, chills, sweating, body aches, loss of appetite, nausea, vomiting"

print("🔬 Generating Malaria Diagnosis Report from Knowledge Base...")
print("=" * 70)

diagnosis = engine.get_ai_diagnosis(symptoms, patient)

print(f"\n✅ DIAGNOSIS: {diagnosis['primary_diagnoses'][0]['condition'] if diagnosis['primary_diagnoses'] else 'Unknown'}")
print(f"💯 CONFIDENCE: {diagnosis['diagnostic_confidence'] * 100:.1f}%")
print(f"🚨 URGENCY: {diagnosis['urgency_level'].upper()}")
print(f"📚 KNOWLEDGE SOURCES USED: {diagnosis['knowledge_sources']} documents")

print("\n📄 TREATMENT RECOMMENDATIONS FROM WHO GUIDELINES:")
for i, treatment in enumerate(diagnosis['treatment_recommendations'][:3], 1):
    print(f"\n{i}. {treatment[:150]}...")

print("\n" + "=" * 70)
print("✅ Report generated successfully using your knowledge base!")
