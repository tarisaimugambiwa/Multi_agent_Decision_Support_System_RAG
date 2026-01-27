"""
AI-Powered Medical Diagnosis Engine
Uses local Ollama API to generate accurate diagnoses with detailed explanations
"""
import json
import requests
from django.conf import settings
from typing import Dict, List, Optional


class DiagnosisEngine:
    """
    Medical diagnosis engine using local Ollama AI with structured output
    """
    
    def __init__(self):
        self.api_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434/api/generate')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')
    
    def generate_diagnosis(
        self,
        symptoms: str,
        vital_signs: Dict,
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None,
        medical_history: Optional[str] = None,
        allergies: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive diagnosis with explanations
        
        Args:
            symptoms: Chief complaints and symptoms description
            vital_signs: Dictionary of vital signs (temperature, weight, BP, etc.)
            patient_age: Patient's age in years
            patient_gender: Patient's gender
            medical_history: Past medical history
            allergies: Known allergies
            
        Returns:
            Dictionary containing diagnosis, explanations, and recommendations
        """
        
        # Build the diagnostic prompt
        prompt = self._build_diagnostic_prompt(
            symptoms=symptoms,
            vital_signs=vital_signs,
            patient_age=patient_age,
            patient_gender=patient_gender,
            medical_history=medical_history,
            allergies=allergies
        )
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1500,  # Reduced for faster generation
                        "num_ctx": 2048  # Limit context window
                    }
                },
                timeout=60  # Reduced timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Parse the response
                diagnosis_data = self._parse_response(response_text)
                return diagnosis_data
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
            
        except Exception as e:
            return {
                "error": str(e),
                "primary_diagnosis": {
                    "condition": "Unable to generate diagnosis",
                    "confidence": 0,
                    "explanation": f"Error occurred: {str(e)}"
                }
            }
    
    def _build_diagnostic_prompt(
        self,
        symptoms: str,
        vital_signs: Dict,
        patient_age: Optional[int],
        patient_gender: Optional[str],
        medical_history: Optional[str],
        allergies: Optional[str]
    ) -> str:
        """Build a comprehensive diagnostic prompt for Ollama AI"""
        
        # Format vital signs
        vital_signs_text = "\n".join([
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in vital_signs.items()
            if value
        ])
        
        prompt = f"""You are an expert medical diagnostician. Analyze the following patient information and provide a comprehensive differential diagnosis.

PATIENT INFORMATION:
- Age: {patient_age if patient_age else 'Not specified'} years
- Gender: {patient_gender if patient_gender else 'Not specified'}
- Known Allergies: {allergies if allergies else 'None reported'}
- Medical History: {medical_history if medical_history else 'No significant history'}

PRESENTING SYMPTOMS:
{symptoms}

VITAL SIGNS:
{vital_signs_text if vital_signs_text else 'No vital signs recorded'}

Provide a detailed medical diagnosis in JSON format with the following structure:
{{
    "primary_diagnosis": {{
        "condition": "Most likely diagnosis name",
        "confidence": 85,
        "explanation": "Detailed explanation of why this diagnosis fits",
        "clinical_reasoning": "Clinical reasoning based on symptoms and signs",
        "supporting_evidence": ["Evidence point 1", "Evidence point 2"]
    }},
    "differential_diagnoses": [
        {{
            "condition": "Alternative diagnosis",
            "confidence": 60,
            "explanation": "Why this is also possible",
            "distinguishing_features": "What would confirm this"
        }}
    ],
    "severity": "Mild/Moderate/Severe/Critical",
    "severity_explanation": "Explanation of severity",
    "red_flags": ["Any concerning signs"],
    "immediate_actions": ["Action 1", "Action 2"],
    "medications": [
        {{
            "name": "Drug name",
            "dosage": "Dosage information",
            "duration": "Treatment duration",
            "instructions": "How to take",
            "contraindications": "Based on allergies"
        }}
    ],
    "follow_up": {{
        "timeline": "When to follow up",
        "monitoring": "What to monitor",
        "warning_signs": "When to seek immediate care"
    }}
}}

Respond with ONLY valid JSON, no other text."""

        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Ollama's response into structured data"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
                diagnosis_data = json.loads(json_text)
                return diagnosis_data
            else:
                return {
                    "primary_diagnosis": {
                        "condition": "Unable to parse diagnosis",
                        "confidence": 0,
                        "explanation": response_text
                    },
                    "differential_diagnoses": [],
                    "severity": "Unknown",
                    "immediate_actions": [],
                    "medications": []
                }
                
        except json.JSONDecodeError:
            return {
                "primary_diagnosis": {
                    "condition": "Diagnosis generated (parsing error)",
                    "confidence": 50,
                    "explanation": response_text
                },
                "differential_diagnoses": [],
                "severity": "Unknown",
                "immediate_actions": ["Consult with physician"],
                "medications": []
            }


def get_diagnosis_for_case(case) -> Dict:
    """
    Convenience function to get diagnosis for a Case object
    
    Args:
        case: Case model instance
        
    Returns:
        Dictionary with diagnosis information
    """
    engine = DiagnosisEngine()
    
    # Extract vital signs from case
    vital_signs = {}
    if hasattr(case, 'vital_signs') and case.vital_signs:
        try:
            vital_signs = json.loads(case.vital_signs) if isinstance(case.vital_signs, str) else case.vital_signs
        except:
            vital_signs = {}
    
    # Get patient information
    patient = case.patient
    patient_age = patient.age if hasattr(patient, 'age') else None
    patient_gender = patient.gender if hasattr(patient, 'gender') else None
    medical_history = patient.medical_history if hasattr(patient, 'medical_history') else None
    allergies = patient.allergies if hasattr(patient, 'allergies') else None
    
    # Generate diagnosis
    diagnosis = engine.generate_diagnosis(
        symptoms=case.symptoms,
        vital_signs=vital_signs,
        patient_age=patient_age,
        patient_gender=patient_gender,
        medical_history=medical_history,
        allergies=allergies
    )
    
    return diagnosis