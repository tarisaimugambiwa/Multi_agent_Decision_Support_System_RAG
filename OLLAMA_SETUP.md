# Ollama Integration Setup Guide

## Overview

This guide explains how to integrate Ollama (local LLM) with your Medical AI Diagnostic System to get AI-powered reasoning based on your knowledge base.

---

## What is Ollama?

Ollama is a tool that lets you run large language models (LLMs) locally on your computer. This means:
- ✅ **Privacy**: Patient data never leaves your server
- ✅ **No API costs**: Completely free to use
- ✅ **Offline**: Works without internet connection
- ✅ **Fast**: Local inference is quick
- ✅ **Customizable**: Choose different medical models

---

## Installation Steps

### Step 1: Install Ollama

**Windows:**
1. Download Ollama from: https://ollama.ai/download
2. Run the installer (OllamaSetup.exe)
3. Follow the installation wizard
4. Ollama will automatically start as a background service

**Verify Installation:**
```powershell
ollama --version
```

You should see the version number (e.g., `ollama version 0.1.17`)

---

### Step 2: Download a Medical Language Model

**Recommended Models:**

1. **Llama 3.2** (Best balance, default)
   ```powershell
   ollama pull llama3.2
   ```
   - Size: ~2GB
   - Quality: Excellent
   - Speed: Fast

2. **Llama 3.1** (Larger, more powerful)
   ```powershell
   ollama pull llama3.1:8b
   ```
   - Size: ~4.7GB
   - Quality: Better reasoning
   - Speed: Moderate

3. **Mistral** (Alternative)
   ```powershell
   ollama pull mistral
   ```
   - Size: ~4.1GB
   - Quality: Good
   - Speed: Fast

4. **Meditron** (Medical-specific, experimental)
   ```powershell
   ollama pull meditron
   ```
   - Size: ~4GB
   - Quality: Medical-trained
   - Speed: Moderate

**For this system, we recommend starting with `llama3.2`**

---

### Step 3: Start Ollama Service

Ollama usually starts automatically. To manually start it:

```powershell
ollama serve
```

To verify it's running:
```powershell
# Test if Ollama API is accessible
curl http://localhost:11434/api/version
```

You should see JSON output with version information.

---

### Step 4: Configure Django Settings

The system is already configured in `medical_ai/settings.py`:

```python
# AI/LLM Settings
OLLAMA_API_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3.2'  # Change to your preferred model
```

**To change the model**, edit `settings.py`:
```python
OLLAMA_MODEL = 'llama3.1:8b'  # or 'mistral', 'meditron', etc.
```

---

## How It Works

### Diagnosis Flow with Ollama

1. **Patient Case Submitted**
   - Nurse/Doctor enters symptoms
   
2. **Knowledge Base Query** (RAG)
   - System searches your 12 medical documents
   - Retrieves top 5 relevant chunks (WHO, Uganda MOH, ESPGHAN, etc.)
   
3. **Rule-Based Matching**
   - Applies symptom pattern matching
   - Generates initial diagnoses with confidence scores
   
4. **Ollama AI Reasoning**
   - Sends prompt with:
     - Patient symptoms
     - Medical history
     - Vital signs
     - Retrieved knowledge base context
   - Ollama analyzes and provides:
     - Primary diagnosis
     - Differential diagnoses
     - Treatment recommendations
     - Red flags
     - Reasoning explanation
     - Confidence score
   
5. **Result Combination**
   - Merges rule-based + AI diagnoses
   - Boosts confidence if both agree
   - Returns comprehensive report

---

## Testing the Integration

### Test 1: Check Ollama Status

```powershell
python test_ollama_diagnosis.py
```

This will:
- ✅ Test connection to Ollama
- ✅ Run a malaria case diagnosis
- ✅ Show AI reasoning
- ✅ Display knowledge base usage

### Test 2: Web Interface

1. Start the server:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python manage.py runserver 8001
   ```

2. Go to: http://127.0.0.1:8001/

3. Create a case with these symptoms:
   ```
   High fever for 2 days, severe headache, chills, sweating, 
   body aches, loss of appetite, nausea, vomiting
   ```

4. Check the diagnosis report - you should see:
   - High confidence diagnosis (e.g., 85% for Malaria)
   - AI reasoning explanation
   - Knowledge base references
   - Treatment recommendations

---

## Prompt Used

The system uses this enhanced prompt (from `diagnoses/ai_utils.py`):

```
You are an experienced medical AI assistant helping healthcare workers in rural Zimbabwe.

Patient Information:
- Age: {age}
- Gender: {gender}
- Symptoms: {symptoms}
- Vital Signs: {vital_signs}
- Medical History: {medical_history}

Relevant Medical Knowledge:
{retrieved_context from WHO, Uganda MOH, etc.}

Based on the patient information and medical knowledge provided, please:
1. Provide a differential diagnosis with the most likely conditions
2. Suggest appropriate treatment recommendations
3. Indicate any red flags that require immediate attention
4. Recommend follow-up care or referral if necessary
5. Provide a confidence score (0-100) for your assessment

Format your response as structured JSON with the following fields:
- primary_diagnosis
- differential_diagnoses
- treatment_plan
- red_flags
- follow_up_recommendations
- confidence_score
- reasoning
```

---

## Troubleshooting

### Issue 1: "Ollama is NOT running"

**Solution:**
```powershell
# Start Ollama service
ollama serve
```

Keep this terminal open. Open a new terminal for other commands.

---

### Issue 2: "Model not found"

**Solution:**
```powershell
# Download the model
ollama pull llama3.2

# Verify models installed
ollama list
```

---

### Issue 3: Low confidence scores

**Possible causes:**
1. Ollama not running → System falls back to rule-based only
2. Model not optimal → Try a larger model (llama3.1:8b)
3. Symptoms unclear → Provide more specific symptoms

**Check:**
```powershell
python test_ollama_diagnosis.py
```

Look for "✅ Ollama is running" at the end.

---

### Issue 4: Slow responses

**Solutions:**
1. Use a smaller model:
   ```powershell
   ollama pull llama3.2
   ```
   Change `OLLAMA_MODEL = 'llama3.2'` in settings

2. Upgrade hardware (GPU helps)

3. Reduce context size (edit `ai_utils.py` to use fewer knowledge chunks)

---

### Issue 5: Connection refused

**Check port:**
```powershell
netstat -ano | findstr :11434
```

If nothing appears, Ollama is not running.

**Restart Ollama:**
```powershell
# Stop any existing instance
taskkill /F /IM ollama.exe

# Start fresh
ollama serve
```

---

## Performance Optimization

### For Better AI Reasoning:

1. **Use Larger Models** (if you have RAM):
   ```powershell
   ollama pull llama3.1:70b  # Requires 40GB+ RAM
   ```

2. **Fine-tune on Medical Data** (advanced):
   - Create a Modelfile with medical examples
   - Use `ollama create` to make custom model

3. **Adjust Temperature** (in code):
   ```python
   # In ai_utils.py _query_ollama_api method
   payload = {
       "model": ollama_model,
       "prompt": prompt,
       "stream": False,
       "format": "json",
       "options": {
           "temperature": 0.3  # Lower = more focused/consistent
       }
   }
   ```

---

## Model Comparison

| Model | Size | RAM Needed | Speed | Medical Quality |
|-------|------|------------|-------|-----------------|
| llama3.2 | 2GB | 8GB | Fast | Good |
| llama3.1:8b | 4.7GB | 16GB | Medium | Very Good |
| llama3.1:70b | 40GB | 64GB | Slow | Excellent |
| mistral | 4.1GB | 16GB | Fast | Good |
| meditron | 4GB | 16GB | Medium | Specialized |

---

## Benefits of Ollama Integration

### Before (Rule-based only):
```
Diagnosis: Malaria
Confidence: 72%
Reasoning: Symptom pattern match
```

### After (Ollama + Knowledge Base):
```
Diagnosis: Malaria  
Confidence: 95% ✓ AI Confirmed
Reasoning: Classic presentation of Plasmodium falciparum malaria 
in a child from an endemic area. High fever (39.8°C), rigors, 
headache, and GI symptoms align with WHO guidelines. The patient's 
age and location (malaria-endemic) are significant risk factors. 
Uganda Ministry of Health protocols recommend immediate antimalarial 
therapy. No signs of severe malaria complications currently, but 
close monitoring is essential.

Treatment Plan:
- Artemisinin-based combination therapy (ACT) per WHO guidelines
- Supportive care: antipyretics, oral rehydration
- Monitor for danger signs: convulsions, altered consciousness
- Follow-up in 48 hours to assess response

Red Flags:
- Persistent high fever after 48 hours
- Development of neurological symptoms
- Signs of severe anemia (pallor, weakness)
```

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Download llama3.2 model
3. ✅ Run test script: `python test_ollama_diagnosis.py`
4. ✅ Try web interface: http://127.0.0.1:8001/
5. ✅ Review diagnosis reports with AI reasoning

---

## Support

- **Ollama Documentation**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Model Library**: https://ollama.ai/library
- **Community**: https://discord.gg/ollama

---

*This integration combines rule-based diagnostic patterns with AI-powered reasoning, all grounded in your WHO/CDC/ESPGHAN knowledge base for evidence-based medical diagnosis.*
