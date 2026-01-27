"""
Quick test of Ollama diagnosis for the specific case: headache, sore throat, runny nose
"""
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from django.conf import settings

# Test Ollama with actual symptoms from the case
symptoms = "headache, sore throat, runny nose for three days now"

prompt = f"""You are an expert medical diagnostician. Analyze the following patient information:

PATIENT INFORMATION:
- Age: 25 years
- Gender: Male
- Temperature: 36.7°C (normal)
- Symptoms: {symptoms}

Provide a diagnosis in JSON format:
{{
    "primary_diagnosis": "Diagnosis name",
    "confidence_score": 85,
    "diagnosis_explanation": "Simple explanation of what this condition is and why the patient has it",
    "reasoning": "Clinical reasoning",
    "differential_diagnoses": ["Alt diagnosis 1", "Alt diagnosis 2"]
}}

Respond with ONLY valid JSON."""

print("Testing Ollama API...")
print(f"API URL: {settings.OLLAMA_API_URL}")
print(f"Model: {settings.OLLAMA_MODEL}")
print(f"\nSymptoms: {symptoms}\n")

try:
    response = requests.post(
        settings.OLLAMA_API_URL,
        json={
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1000
            },
            "format": "json"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result.get('response', '')
        print("✅ Ollama Response:")
        print(ai_response)
        
        # Try to parse as JSON
        import json
        try:
            parsed = json.loads(ai_response)
            print("\n✅ Parsed JSON:")
            print(f"  Diagnosis: {parsed.get('primary_diagnosis')}")
            print(f"  Confidence: {parsed.get('confidence_score')}%")
            print(f"  Explanation: {parsed.get('diagnosis_explanation')}")
        except:
            print("\n⚠️ Response is not valid JSON")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Ollama")
    print("Make sure Ollama is running: ollama serve")
except Exception as e:
    print(f"❌ Error: {e}")
