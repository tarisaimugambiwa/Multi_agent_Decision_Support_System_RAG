#!/usr/bin/env python
"""
Test Ollama Integration with Knowledge Base
This script tests AI diagnosis with Ollama reasoning
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from diagnoses.ai_utils import MedicalAIDiagnosticEngine

# Initialize diagnostic engine
engine = MedicalAIDiagnosticEngine()

print("="*80)
print("🤖 TESTING OLLAMA INTEGRATION WITH KNOWLEDGE BASE")
print("="*80)

# Test Case: Malaria symptoms
test_case = {
    'symptoms': 'High fever for 2 days, severe headache, chills, sweating, body aches, loss of appetite, nausea, vomiting',
    'patient_history': {
        'age': 3,
        'gender': 'Female',
        'medical_history': 'Lives in malaria-endemic area, no prior malaria episodes',
        'vital_signs': {
            'temperature': '39.8°C',
            'heart_rate': '130/min',
            'respiratory_rate': '32/min'
        }
    }
}

print("\n📋 Test Case: Malaria Symptoms")
print(f"   Patient: 3-year-old female")
print(f"   Symptoms: {test_case['symptoms'][:80]}...")
print(f"   History: {test_case['patient_history']['medical_history']}")
print("\n" + "="*80)

print("\n🔍 Running AI Diagnosis with Ollama + Knowledge Base...")
print("   Step 1: Querying knowledge base for relevant information...")
print("   Step 2: Applying rule-based diagnostic matching...")
print("   Step 3: Sending to Ollama for AI reasoning...")
print("   Step 4: Combining results...")

# Run diagnosis
result = engine.get_ai_diagnosis(
    test_case['symptoms'],
    test_case['patient_history']
)

print("\n" + "="*80)
print("📊 DIAGNOSIS RESULTS")
print("="*80)

# Display primary diagnoses
print("\n🎯 Primary Diagnoses:")
if result['primary_diagnoses']:
    for i, diagnosis in enumerate(result['primary_diagnoses'][:3], 1):
        confidence_pct = diagnosis['confidence'] * 100
        ai_confirmed = " ✓ AI Confirmed" if diagnosis.get('ai_confirmed') else ""
        print(f"\n   {i}. {diagnosis['condition']}")
        print(f"      Confidence: {confidence_pct:.1f}%{ai_confirmed}")
        print(f"      Reasoning: {diagnosis.get('reasoning', 'N/A')}")
        print(f"      Urgency: {diagnosis.get('urgency', 'N/A').upper()}")
else:
    print("   No high-confidence diagnoses found")

# Display AI reasoning from Ollama
if result.get('ai_diagnosis'):
    print("\n🤖 Ollama AI Analysis:")
    print(f"   Diagnosis: {result['ai_diagnosis']}")
    
    if result.get('ai_reasoning'):
        print(f"\n   Reasoning: {result['ai_reasoning']}")
    
    if result.get('ai_confidence'):
        print(f"   AI Confidence: {result['ai_confidence']*100:.1f}%")

# Display severity and urgency
print(f"\n⚠️  Severity Score: {result['severity_score']:.2f}")
print(f"🚨 Urgency Level: {result['urgency_level'].upper()}")

# Display treatment recommendations
if result['treatment_recommendations']:
    print("\n💊 Treatment Recommendations:")
    for i, treatment in enumerate(result['treatment_recommendations'][:3], 1):
        print(f"\n   {i}. {treatment}")

# Display knowledge sources
print(f"\n📚 Knowledge Base Sources Consulted: {result['knowledge_sources']}")

# Display recommendations
if result['recommendations']:
    print("\n📋 Clinical Recommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"   {i}. {rec}")

print("\n" + "="*80)
print("✅ Test Complete!")
print("="*80)

# Check Ollama status
print("\n🔧 Ollama Status Check:")
try:
    import requests
    response = requests.get('http://localhost:11434/api/version', timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama is running")
        version_info = response.json()
        print(f"   Version: {version_info.get('version', 'unknown')}")
    else:
        print("   ⚠️  Ollama responded but with unexpected status")
except requests.exceptions.ConnectionError:
    print("   ❌ Ollama is NOT running")
    print("\n   To install and run Ollama:")
    print("   1. Download from: https://ollama.ai/")
    print("   2. Install Ollama")
    print("   3. Run: ollama pull llama3.2")
    print("   4. Run: ollama serve")
    print("\n   The system will still work with rule-based diagnosis,")
    print("   but AI reasoning will not be available.")
except Exception as e:
    print(f"   ⚠️  Error checking Ollama: {e}")

print("\n" + "="*80)
print("\n📊 Full Diagnosis JSON:")
print(json.dumps(result, indent=2, default=str))
