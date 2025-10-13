# Prompt Engineering Update

## Summary
Enhanced the AI diagnosis prompt to provide more structured, comprehensive, and context-aware medical assessments for the rural Zimbabwe healthcare setting.

## Changes Made

### 1. Added DIAGNOSIS_PROMPT Constant (`diagnoses/ai_utils.py` lines 16-47)

Created a reusable prompt template as a module-level constant for better maintainability:

```python
DIAGNOSIS_PROMPT = """
You are an experienced medical AI assistant helping healthcare workers in rural Zimbabwe.

Patient Information:
- Age: {age}
- Gender: {gender}
- Symptoms: {symptoms}
- Vital Signs: {vital_signs}
- Medical History: {medical_history}

Relevant Medical Knowledge:
{retrieved_context}

Based on the patient information and medical knowledge provided, please:
1. Provide a differential diagnosis with the most likely conditions
2. Suggest appropriate treatment recommendations
3. Indicate any red flags that require immediate attention
4. Recommend follow-up care or referral if necessary
5. Provide a confidence score (0-100) for your assessment

Format your response as structured JSON with the following fields:
- primary_diagnosis: The most likely condition
- differential_diagnoses: List of other possible conditions
- treatment_plan: Recommended treatments and medications
- red_flags: Any warning signs requiring immediate attention
- follow_up_recommendations: Next steps and follow-up care
- confidence_score: Your confidence in this assessment (0-100)
- reasoning: Brief explanation of your diagnostic reasoning
"""
```

### 2. Updated `_format_medical_prompt` Method

**Location**: `diagnoses/ai_utils.py` lines 310-345

**Changes**:
- Increased knowledge context from 3 to 5 most relevant chunks
- Increased context length from 200 to 300 characters per chunk
- Added vital signs extraction and formatting
- Uses the DIAGNOSIS_PROMPT template with `.format()` for cleaner code
- Template now includes all key patient information

**Before**:
```python
prompt = f"""
Medical Case Analysis:
Patient Information:
- Age: {patient_history.get('age', 'Unknown')}
- Gender: {patient_history.get('gender', 'Unknown')}
...
Please provide a brief medical assessment focusing on:
1. Most likely diagnosis
2. Key diagnostic considerations
3. Recommended immediate actions
"""
```

**After**:
```python
prompt = DIAGNOSIS_PROMPT.format(
    age=patient_history.get('age', 'Unknown'),
    gender=patient_history.get('gender', 'Unknown'),
    symptoms=symptoms,
    vital_signs=vital_signs,
    medical_history=patient_history.get('medical_history', 'None reported'),
    retrieved_context='\n'.join(relevant_info)
)
```

## Improvements

### 1. **Context-Aware Design**
- Explicitly mentions "rural Zimbabwe" to help the AI consider resource constraints
- Tailored for healthcare workers in resource-limited settings

### 2. **Enhanced Input Processing**
- **More Knowledge Context**: 5 chunks instead of 3 (67% increase)
- **Longer Chunks**: 300 characters instead of 200 (50% increase)
- **Vital Signs**: Now explicitly included in the prompt
- **Structured Format**: Uses template variables for cleaner, more maintainable code

### 3. **Structured JSON Output**
The prompt now requests a structured JSON response with specific fields:
- `primary_diagnosis`: Most likely condition
- `differential_diagnoses`: Alternative possibilities
- `treatment_plan`: Actionable treatment recommendations
- `red_flags`: Critical warning signs
- `follow_up_recommendations`: Next steps for patient care
- `confidence_score`: AI's confidence (0-100)
- `reasoning`: Diagnostic reasoning explanation

### 4. **Comprehensive Assessment Criteria**
The prompt explicitly asks the AI to consider:
1. Differential diagnosis (multiple possibilities)
2. Treatment recommendations (actionable advice)
3. Red flags (safety-critical information)
4. Follow-up care (continuity of care)
5. Confidence scoring (transparency about uncertainty)

### 5. **Better Maintainability**
- Prompt is now a module-level constant
- Easy to update in one place
- Template-based formatting (`.format()`) is cleaner than f-strings
- Separated concerns: prompt definition vs. data formatting

## Benefits

### For Healthcare Workers
- More comprehensive diagnostic information
- Clear red flag identification
- Actionable treatment plans
- Confidence scores help with decision-making
- Follow-up recommendations improve continuity of care

### For AI Performance
- Structured output format improves parsing reliability
- Context-aware prompting improves relevance
- More knowledge context improves accuracy
- Explicit instructions reduce ambiguity

### For Developers
- Single source of truth for the prompt
- Easy to modify and test
- Template variables clearly show what data is needed
- Better code organization and readability

## Testing Recommendations

1. **Test with Various Symptoms**:
   - Simple cases (e.g., "fever and cough")
   - Complex cases (e.g., multiple symptoms)
   - Emergency cases (e.g., chest pain)

2. **Verify JSON Output**:
   - Check that AI responses are valid JSON
   - Ensure all required fields are present
   - Validate confidence scores are 0-100

3. **Check Context Usage**:
   - Verify knowledge base content is being used
   - Ensure vital signs are appearing in prompts
   - Confirm medical history is included

4. **Evaluate Response Quality**:
   - Are differential diagnoses relevant?
   - Are red flags correctly identified?
   - Are treatment plans appropriate for rural settings?
   - Is reasoning clear and medically sound?

## Future Enhancements

1. **Dynamic Prompt Adjustment**: Adjust prompt based on urgency level
2. **Few-Shot Examples**: Add example diagnoses to improve output format
3. **Cultural Context**: Add more specific regional disease information
4. **Language Support**: Multi-language prompt templates
5. **Prompt Versioning**: Track prompt changes and A/B test improvements

## Related Files

- `diagnoses/ai_utils.py`: Main diagnostic engine with prompt
- `diagnoses/services/diagnosis_agent.py`: Uses the diagnostic engine
- `knowledge/rag_utils.py`: Provides medical knowledge context

## Impact

This update significantly improves the quality and structure of AI-generated diagnoses, making them more actionable and reliable for healthcare workers in rural Zimbabwe. The structured JSON output also makes it easier to integrate the AI's recommendations into the user interface and workflow.
