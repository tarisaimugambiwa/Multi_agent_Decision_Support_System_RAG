"""
Utility functions for the diagnoses app
"""
from typing import Dict, List
import json


def format_diagnosis_for_display(diagnosis_data: Dict) -> Dict:
    """
    Format the AI diagnosis data for template display
    """
    
    primary = diagnosis_data.get('primary_diagnosis', {})
    
    formatted = {
        'primary_diagnosis': primary.get('condition', 'Unknown'),
        'confidence': primary.get('confidence', 0),
        'explanation': primary.get('explanation', ''),
        'clinical_reasoning': primary.get('clinical_reasoning', ''),
        'supporting_evidence': primary.get('supporting_evidence', []),
        'differential_diagnoses': diagnosis_data.get('differential_diagnoses', []),
        'severity': diagnosis_data.get('severity', 'Unknown'),
        'severity_explanation': diagnosis_data.get('severity_explanation', ''),
        'red_flags': diagnosis_data.get('red_flags', []),
        'immediate_actions': diagnosis_data.get('immediate_actions', []),
        'medications': diagnosis_data.get('medications', []),
        'follow_up': diagnosis_data.get('follow_up', {}),
    }
    
    return formatted


def calculate_symptom_severity(symptoms: str, vital_signs: Dict) -> str:
    """
    Basic severity assessment based on keywords and vital signs
    """
    
    # Check for critical keywords
    critical_keywords = [
        'unconscious', 'unresponsive', 'severe bleeding', 'chest pain',
        'difficulty breathing', 'seizure', 'stroke symptoms'
    ]
    
    severe_keywords = [
        'severe pain', 'high fever', 'persistent vomiting',
        'severe headache', 'confusion'
    ]
    
    symptoms_lower = symptoms.lower()
    
    # Check vital signs
    try:
        temp = float(vital_signs.get('temperature', 0))
        if temp >= 39.5 or temp <= 35:
            return 'Severe'
        elif temp >= 38.5:
            return 'Moderate'
    except (ValueError, TypeError):
        pass
    
    # Check keywords
    if any(keyword in symptoms_lower for keyword in critical_keywords):
        return 'Critical'
    
    if any(keyword in symptoms_lower for keyword in severe_keywords):
        return 'Severe'
    
    if 'weeks' in symptoms_lower or 'months' in symptoms_lower:
        return 'Moderate'
    
    return 'Mild'


def generate_case_report_pdf(case):
    """
    Generate a PDF report for a case
    Returns the file path or None if failed
    """
    # Placeholder - implement PDF generation as needed
    # You can use libraries like reportlab or weasyprint
    return None