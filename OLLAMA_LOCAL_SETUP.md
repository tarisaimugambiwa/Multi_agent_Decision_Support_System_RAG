# Ollama Setup Guide for Multi-Agent Medical System

## ✅ System Updated to Use Local Ollama

Your multi-agent medical decision support system now uses **local Ollama** instead of external APIs (Claude/DeepSeek). This provides:

- ✅ **Complete Privacy** - All data stays on your machine
- ✅ **No API Costs** - Free unlimited usage
- ✅ **Offline Capability** - Works without internet
- ✅ **Customizable Models** - Choose medical-specific or general models
- ✅ **Fast Response** - Local processing

---

## 🚀 Quick Setup

### 1. Install Ollama

**Windows:**
```powershell
# Download installer from https://ollama.ai/download
# Run the installer
# Ollama will start automatically
```

**Verify Installation:**
```powershell
ollama --version
```

### 2. Pull a Model

**Recommended Models:**

```powershell
# Option 1: Llama 3.2 (Default - Good balance)
ollama pull llama3.2

# Option 2: Llama 3.1 8B (Better accuracy, needs more RAM)
ollama pull llama3.1:8b

# Option 3: Mistral (Fast and efficient)
ollama pull mistral

# Option 4: Meditron (Medical-specific model)
ollama pull meditron
```

### 3. Start Ollama Service

```powershell
ollama serve
```

Keep this running while using the medical system.

### 4. Test the Connection

```powershell
# Quick test
ollama run llama3.2 "What are symptoms of pneumonia?"
```

---

## ⚙️ Configuration

Your system is configured in [`medical_ai/settings.py`](medical_ai/settings.py):

```python
# Ollama Configuration (Local AI)
OLLAMA_API_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3.2'  # Change to your preferred model
```

### Change the Model

Edit `settings.py`:

```python
# For better accuracy (requires ~8GB RAM):
OLLAMA_MODEL = 'llama3.1:8b'

# For medical-specific knowledge:
OLLAMA_MODEL = 'meditron'

# For faster responses:
OLLAMA_MODEL = 'mistral'
```

---

## 📊 Model Comparison

| Model | Size | Speed | Medical Accuracy | RAM Required |
|-------|------|-------|-----------------|--------------|
| **llama3.2** | 2GB | ⚡⚡⚡ Fast | Good | 4GB |
| **llama3.1:8b** | 4.7GB | ⚡⚡ Medium | Excellent | 8GB |
| **mistral** | 4.1GB | ⚡⚡⚡ Fast | Good | 6GB |
| **meditron** | 3.8GB | ⚡⚡ Medium | Excellent | 6GB |

**Recommendation**: Start with `llama3.2`, upgrade to `llama3.1:8b` or `meditron` for better medical reasoning.

---

## 🔧 Usage in Your System

The system automatically uses Ollama when:

1. Creating a new case with symptoms
2. Generating AI diagnosis
3. Creating treatment recommendations

### Where Ollama is Used:

**File: [`diagnoses/ai_diagnosis.py`](diagnoses/ai_diagnosis.py)**
```python
class DiagnosisEngine:
    def __init__(self):
        self.api_url = 'http://localhost:11434/api/generate'
        self.model = 'llama3.2'
    
    def generate_diagnosis(self, symptoms, vital_signs, ...):
        # Calls local Ollama API
        response = requests.post(self.api_url, json={
            "model": self.model,
            "prompt": prompt,
            ...
        })
```

**File: [`diagnoses/ai_utils.py`](diagnoses/ai_utils.py)**
```python
def _query_ollama_api(self, prompt):
    # Query local Ollama for AI-powered diagnosis
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={"model": "llama3.2", "prompt": prompt}
    )
```

---

## 🧪 Test Your Setup

Run the test script:

```powershell
python test_ollama_diagnosis.py
```

Expected output:
```
🤖 TESTING OLLAMA INTEGRATION WITH KNOWLEDGE BASE
================================================

📋 Test Case: Child with fever and cough

🔍 Running AI Diagnosis with Ollama + Knowledge Base...
   Step 1: Searching medical knowledge base...
   Step 2: Found 5 relevant medical documents
   Step 3: Sending to Ollama for AI reasoning...

✅ Diagnosis Generated Successfully!

🎯 Primary Diagnosis: Pneumonia
   Confidence: 85%
   Urgency: High

🤖 Ollama AI Analysis:
   Based on the symptoms and medical guidelines...
```

---

## 🐛 Troubleshooting

### Ollama Not Running
```powershell
# Error: Connection refused
# Solution: Start Ollama
ollama serve
```

### Model Not Found
```powershell
# Error: model 'llama3.2' not found
# Solution: Pull the model
ollama pull llama3.2
```

### Slow Responses
```powershell
# Switch to a smaller/faster model
ollama pull mistral

# Update settings.py
OLLAMA_MODEL = 'mistral'
```

### Out of Memory
```powershell
# Use smaller model
ollama pull llama3.2

# Update settings.py
OLLAMA_MODEL = 'llama3.2'
```

---

## 🔄 Starting Your System

1. **Start Ollama** (in one terminal):
```powershell
ollama serve
```

2. **Start Django** (in another terminal):
```powershell
python manage.py runserver
```

3. **Access System**:
```
https://127.0.0.1:8000
```

---

## 📈 Performance Tips

### 1. **GPU Acceleration** (if available)
Ollama automatically uses GPU if detected. Check with:
```powershell
ollama ps
```

### 2. **Increase Context Window**
For longer patient histories, edit the API call to increase context:
```python
"options": {
    "num_ctx": 4096  # Increase from default 2048
}
```

### 3. **Adjust Temperature**
For more consistent diagnoses:
```python
"options": {
    "temperature": 0.3  # Lower = more consistent
}
```

---

## 🌟 Advanced: Medical-Specific Models

### Meditron (Medical AI)
```powershell
# Pull medical-specific model
ollama pull meditron

# Update settings
OLLAMA_MODEL = 'meditron'
```

Meditron is trained on medical literature and provides better medical reasoning.

---

## ✅ Benefits Over Cloud APIs

| Feature | Ollama (Local) | Cloud APIs |
|---------|---------------|------------|
| **Privacy** | ✅ Complete | ❌ Data sent externally |
| **Cost** | ✅ Free | 💰 Pay per request |
| **Internet** | ✅ Offline | ❌ Requires connection |
| **Speed** | ✅ Fast (local) | ⚠️ Network latency |
| **Customization** | ✅ Full control | ❌ Limited |
| **Updates** | ✅ Anytime | ❌ Depends on provider |

---

## 📚 Resources

- **Ollama Documentation**: https://ollama.ai/docs
- **Model Library**: https://ollama.ai/library
- **Meditron Model**: https://ollama.ai/library/meditron
- **Llama 3.2 Model**: https://ollama.ai/library/llama3.2

---

## 🎯 Your System is Ready!

Your multi-agent medical diagnosis system now runs completely locally with Ollama. All AI reasoning happens on your machine with full privacy and no API costs.

**Next Steps:**
1. Start Ollama: `ollama serve`
2. Test connection: `python test_ollama_diagnosis.py`
3. Start Django: `python manage.py runserver`
4. Create a case and see Ollama-powered diagnosis in action!
