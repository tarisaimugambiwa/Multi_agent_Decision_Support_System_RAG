import requests
import json
import time

def test_ollama_speed():
    """Test Ollama response time"""
    
    # Simple test
    print("Testing Ollama with simple query...")
    start = time.time()
    r = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama3.2',
        'prompt': 'What is 2+2? Answer in one word.',
        'stream': False,
        'options': {'num_predict': 10}
    })
    elapsed = time.time() - start
    print(f"Simple query took: {elapsed:.2f}s")
    print(f"Response: {r.json().get('response', 'No response')}\n")
    
    # Medical diagnosis test (similar to actual usage)
    print("Testing Ollama with medical diagnosis query...")
    medical_prompt = """Analyze these symptoms and provide a diagnosis:
Symptoms: headache, sore throat, runny nose for three days
Temperature: 36.7°C (normal)

Provide your response in JSON format:
{
    "primary_diagnosis": "diagnosis name",
    "confidence": 0.X,
    "explanation": "brief explanation"
}
"""
    
    start = time.time()
    r = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama3.2',
        'prompt': medical_prompt,
        'stream': False,
        'format': 'json',
        'options': {
            'temperature': 0.7,
            'num_predict': 1000,
            'num_ctx': 2048
        }
    }, timeout=120)
    elapsed = time.time() - start
    
    print(f"Medical query took: {elapsed:.2f}s")
    if r.status_code == 200:
        response_text = r.json().get('response', '')
        print(f"Response length: {len(response_text)} chars")
        print(f"Response:\n{response_text}\n")
        
        # Try to parse JSON
        try:
            diagnosis = json.loads(response_text)
            print(f"Diagnosis: {diagnosis.get('primary_diagnosis', 'Unknown')}")
            print(f"Confidence: {diagnosis.get('confidence', 0)}")
            print(f"Explanation: {diagnosis.get('explanation', 'None')}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == '__main__':
    test_ollama_speed()
