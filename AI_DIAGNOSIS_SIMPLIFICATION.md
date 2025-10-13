# AI Diagnosis Report Simplification for Nurses

## Overview
Simplified the AI diagnosis report to be more nurse-friendly by:
1. Removing confusing medical terminology and differential diagnoses
2. Adding plain language explanations of diagnoses
3. Hiding technical knowledge base references from nurses
4. Keeping recommended tests visible only to doctors

## Changes Made

### 1. Template Updates (`templates/diagnoses/case_detail.html`)

#### Simplified AI Diagnosis Section (Lines 286-360)
**Before:**
- Showed "Differential Diagnoses" with probability percentages
- Used medical jargon without explanation
- Displayed all diagnostic tests to everyone

**After:**
- **Primary Diagnosis** with plain language explanation
- **"What This Means"** section explaining the diagnosis in simple terms
- **AI Confidence Level** with visual progress bar
- **Emergency Alert** with clear action required messaging
- **Important Warning Signs** (red flags) in easy-to-understand format
- **Recommended Tests** only visible to doctors (`{% if user.role == 'DOCTOR' %}`)

#### Hidden Knowledge Base References (Lines 490-510)
**Before:**
- Medical Knowledge References visible to all users

**After:**
- Only visible to doctors and experts: `{% if user.role != 'NURSE' %}`
- Nurses don't see technical document references

### 2. AI Prompt Engineering (`diagnoses/ai_utils.py`)

#### Updated DIAGNOSIS_PROMPT (Lines 17-43)
**Added:**
```python
6. Explain the diagnosis in simple language that a nurse can understand and explain to the patient
```

**New JSON Field:**
```json
"diagnosis_explanation": "A clear, simple explanation of what this condition means, 
                          what causes it, and why you think the patient has it. 
                          Write this in plain language that anyone can understand, 
                          avoiding medical jargon."
```

#### Extract Explanation from Ollama Response (Lines 599)
**Added:**
```python
# Extract plain language explanation
diagnosis_explanation = ai_response.get('diagnosis_explanation', '')
```

#### Include Explanation in Diagnosis Result (Lines 668)
**Added:**
```python
'diagnosis_explanation': diagnosis_explanation,  # Plain language explanation for nurses
```

### 3. Diagnosis Agent Updates (`diagnoses/services/diagnosis_agent.py`)

#### Capture Explanation (Lines 267-268)
**Added:**
```python
# Extract plain language explanation
diagnosis_explanation = ai_result.get('diagnosis_explanation', '')
```

#### Return Explanation in Diagnosis Dict (Lines 293)
**Added:**
```python
'explanation': diagnosis_explanation,  # Plain language explanation
```

#### Include in Final Analysis (Line 106)
**Added:**
```python
'explanation': ai_diagnosis.get('explanation', ''),  # Plain language explanation
```

## How It Works

### For Nurses:
1. **Create Case**: Nurse enters symptoms and patient information
2. **AI Processing**: System analyzes using knowledge base + Ollama
3. **View Report**: Nurse sees:
   - ✅ Simple diagnosis name
   - ✅ "What This Means" explanation in plain language
   - ✅ Emergency alerts (if any)
   - ✅ Warning signs to watch for
   - ✅ Treatment plan with actions and medications
   - ❌ Differential diagnoses (removed - too confusing)
   - ❌ Medical knowledge references (hidden - not needed)

### For Doctors:
1. **Review Case**: Doctor sees everything nurses see PLUS:
   - ✅ Recommended diagnostic tests
   - ✅ Medical knowledge base references
   - ✅ Technical evidence sources
   - ✅ Full diagnostic reasoning

## Example Output

### Nurse View:
```
🧠 AI-Powered Diagnosis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Primary Diagnosis: Acute Gastroenteritis

ℹ️ What This Means:
This is an infection or inflammation of the stomach and intestines, 
commonly known as "stomach flu." It's usually caused by eating 
contaminated food or water, or being exposed to someone who is sick. 
The symptoms of nausea, vomiting, and diarrhea suggest this condition 
because they're typical signs of the digestive system being upset.

AI Confidence Level:
[████████░░] 85% Confidence

⚠️ Emergency Alert
⚡ Severe dehydration detected
Action Required: Immediate medical attention needed!

🚩 Important Warning Signs
⚠️ Dehydration: Signs of fluid loss
⚠️ Persistent Vomiting: Unable to keep fluids down
```

### Doctor View (Additional):
```
🧪 Recommended Diagnostic Tests
Complete Blood Count | Stool Culture | Electrolyte Panel

📚 Medical Knowledge References
This diagnosis was informed by 5 medical documents:
📄 WHO_Gastroenteritis_Guidelines_2023.pdf
📄 Treatment_Protocol_Dehydration.pdf
...
```

## Testing Steps

1. **Create a new case as a nurse**:
   - Login as nurse user
   - Fill patient symptoms
   - Click "Create Case & Generate AI Diagnosis"
   - Wait for AI processing (progress modal shows)

2. **Verify the report shows**:
   - ✅ Primary diagnosis with plain explanation
   - ✅ No differential diagnoses section
   - ✅ Treatment recommendations
   - ✅ No knowledge base references

3. **Login as doctor and review same case**:
   - ✅ Should see diagnostic tests
   - ✅ Should see knowledge base references

## Key Benefits

### For Nurses:
- **Easier to understand**: Plain language explanations
- **Less confusion**: No medical jargon or alternative diagnoses
- **Actionable**: Clear treatment steps and warning signs
- **Confident**: Can explain diagnosis to patients

### For System:
- **Role-based access**: Different views for different roles
- **Knowledge base integration**: Still uses medical guidelines
- **AI-powered**: Ollama generates explanations automatically
- **Scalable**: Easy to add more roles or customize views

## Configuration

No configuration changes needed. The system will automatically:
- Generate plain language explanations via Ollama
- Show/hide sections based on user role
- Use medical knowledge base for accuracy

## Next Steps

1. ✅ Template simplified (case_detail.html)
2. ✅ AI prompt updated (ai_utils.py)
3. ✅ Diagnosis agent updated (diagnosis_agent.py)
4. 🔄 Test with real case (create new case as nurse)
5. 🔄 Verify explanation appears in report
6. 🔄 Verify role-based visibility works

## Notes

- The AI (Ollama) may take 30-60 seconds to generate the explanation
- If Ollama is not running, the explanation field will be empty
- The system will still show the diagnosis, just without the explanation
- Ensure Ollama is running: `ollama serve` in terminal
