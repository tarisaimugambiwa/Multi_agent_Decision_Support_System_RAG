"""
AI Diagnosis utilities for Medical AI System
Provides intelligent diagnostic suggestions using RAG and rule-based reasoning
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests
from django.conf import settings

from knowledge.rag_utils import search_medical_knowledge, get_treatment_recommendations, get_diagnostic_guidelines


class MedicalAIDiagnosticEngine:
    """
    AI-powered diagnostic engine combining RAG with rule-based reasoning
    """
    
    def __init__(self):
        self.confidence_threshold = 0.6
        self.max_diagnoses = 3
        
        # Medical condition patterns and weights
        self.symptom_patterns = {
            'cardiac': {
                'keywords': ['chest pain', 'shortness of breath', 'palpitations', 'fatigue', 'dizziness', 'sweating'],
                'severity_indicators': ['severe', 'crushing', 'radiating', 'sudden onset'],
                'weight': 0.8
            },
            'respiratory': {
                'keywords': ['cough', 'shortness of breath', 'wheezing', 'chest tightness', 'sputum'],
                'severity_indicators': ['blood', 'persistent', 'worsening', 'fever'],
                'weight': 0.7
            },
            'gastrointestinal': {
                'keywords': ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'constipation', 'bloating'],
                'severity_indicators': ['blood', 'severe', 'persistent', 'dehydration'],
                'weight': 0.6
            },
            'neurological': {
                'keywords': ['headache', 'dizziness', 'confusion', 'numbness', 'weakness', 'seizure'],
                'severity_indicators': ['sudden', 'severe', 'persistent', 'loss of consciousness'],
                'weight': 0.8
            },
            'infectious': {
                'keywords': ['fever', 'chills', 'fatigue', 'body aches', 'sore throat', 'cough'],
                'severity_indicators': ['high fever', 'persistent', 'worsening', 'difficulty breathing'],
                'weight': 0.5
            }
        }
        
        # Common conditions with diagnostic criteria
        self.condition_rules = {
            'acute_coronary_syndrome': {
                'required_symptoms': ['chest pain'],
                'supporting_symptoms': ['shortness of breath', 'sweating', 'nausea'],
                'risk_factors': ['diabetes', 'hypertension', 'smoking', 'family history'],
                'urgency': 'critical',
                'confidence_boost': 0.3
            },
            'pneumonia': {
                'required_symptoms': ['cough', 'fever'],
                'supporting_symptoms': ['shortness of breath', 'chest pain', 'sputum'],
                'risk_factors': ['age > 65', 'immunocompromised', 'chronic disease'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'gastroenteritis': {
                'required_symptoms': ['diarrhea'],
                'supporting_symptoms': ['nausea', 'vomiting', 'abdominal pain', 'fever'],
                'risk_factors': ['recent travel', 'food poisoning', 'contact'],
                'urgency': 'moderate',
                'confidence_boost': 0.1
            },
            'migraine': {
                'required_symptoms': ['headache'],
                'supporting_symptoms': ['nausea', 'light sensitivity', 'sound sensitivity'],
                'risk_factors': ['family history', 'stress', 'hormonal changes'],
                'urgency': 'low',
                'confidence_boost': 0.1
            }
        }
    
    def _calculate_symptom_severity(self, symptoms: str) -> float:
        """
        Calculate overall symptom severity based on keywords and patterns
        
        Args:
            symptoms (str): Patient symptoms description
            
        Returns:
            float: Severity score (0.0 to 1.0)
        """
        symptoms_lower = symptoms.lower()
        severity_score = 0.0
        total_weight = 0.0
        
        for category, data in self.symptom_patterns.items():
            category_score = 0.0
            
            # Check for symptom keywords
            for keyword in data['keywords']:
                if keyword in symptoms_lower:
                    category_score += 0.2
            
            # Check for severity indicators
            for indicator in data['severity_indicators']:
                if indicator in symptoms_lower:
                    category_score += 0.3
            
            # Weight the category score
            if category_score > 0:
                severity_score += category_score * data['weight']
                total_weight += data['weight']
        
        return min(severity_score / max(total_weight, 1.0), 1.0)
    
    def _match_condition_rules(self, symptoms: str, patient_history: Dict) -> List[Dict]:
        """
        Apply rule-based matching for known conditions
        
        Args:
            symptoms (str): Patient symptoms
            patient_history (Dict): Patient medical history
            
        Returns:
            List[Dict]: Matched conditions with confidence scores
        """
        symptoms_lower = symptoms.lower()
        matched_conditions = []
        
        for condition, rules in self.condition_rules.items():
            confidence = 0.0
            
            # Check required symptoms
            required_met = all(symptom in symptoms_lower for symptom in rules['required_symptoms'])
            if not required_met:
                continue
            
            confidence += 0.4  # Base confidence for meeting requirements
            
            # Check supporting symptoms
            supporting_count = sum(1 for symptom in rules['supporting_symptoms'] 
                                 if symptom in symptoms_lower)
            supporting_ratio = supporting_count / len(rules['supporting_symptoms'])
            confidence += supporting_ratio * 0.3
            
            # Check risk factors from patient history
            risk_factor_count = 0
            for risk_factor in rules['risk_factors']:
                if self._check_risk_factor(risk_factor, patient_history):
                    risk_factor_count += 1
            
            if rules['risk_factors']:
                risk_ratio = risk_factor_count / len(rules['risk_factors'])
                confidence += risk_ratio * 0.2
            
            # Apply confidence boost
            confidence += rules['confidence_boost']
            confidence = min(confidence, 1.0)
            
            if confidence >= self.confidence_threshold:
                matched_conditions.append({
                    'condition': condition.replace('_', ' ').title(),
                    'confidence': confidence,
                    'urgency': rules['urgency'],
                    'supporting_symptoms': supporting_count,
                    'risk_factors': risk_factor_count
                })
        
        return sorted(matched_conditions, key=lambda x: x['confidence'], reverse=True)
    
    def _check_risk_factor(self, risk_factor: str, patient_history: Dict) -> bool:
        """
        Check if patient has specific risk factor
        
        Args:
            risk_factor (str): Risk factor to check
            patient_history (Dict): Patient history data
            
        Returns:
            bool: True if risk factor is present
        """
        history_text = json.dumps(patient_history).lower()
        
        # Simple keyword matching for common risk factors
        risk_mappings = {
            'diabetes': ['diabetes', 'diabetic'],
            'hypertension': ['hypertension', 'high blood pressure'],
            'smoking': ['smoking', 'smoker', 'tobacco'],
            'family history': ['family history', 'hereditary'],
            'age > 65': lambda: patient_history.get('age', 0) > 65,
            'immunocompromised': ['immunocompromised', 'immune deficiency'],
            'chronic disease': ['chronic', 'long-term condition']
        }
        
        if risk_factor in risk_mappings:
            mapping = risk_mappings[risk_factor]
            if callable(mapping):
                return mapping()
            else:
                return any(keyword in history_text for keyword in mapping)
        
        return False
    
    def _query_huggingface_api(self, prompt: str) -> Optional[str]:
        """
        Query Hugging Face API for additional AI insights (optional)
        
        Args:
            prompt (str): Medical prompt for analysis
            
        Returns:
            Optional[str]: AI response or None if API unavailable
        """
        try:
            # Using free Hugging Face Inference API
            # You can get a free API key from https://huggingface.co/
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            
            # Check if API key is available
            hf_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
            if not hf_api_key:
                return None
            
            headers = {"Authorization": f"Bearer {hf_api_key}"}
            payload = {"inputs": prompt}
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
            
        except Exception as e:
            print(f"Error querying Hugging Face API: {str(e)}")
        
        return None
    
    def _format_medical_prompt(self, symptoms: str, patient_history: Dict, knowledge_context: List[Dict]) -> str:
        """
        Format a structured medical prompt for AI analysis
        
        Args:
            symptoms (str): Patient symptoms
            patient_history (Dict): Patient medical history
            knowledge_context (List[Dict]): Retrieved medical knowledge
            
        Returns:
            str: Formatted medical prompt
        """
        # Extract key information from knowledge context
        relevant_info = []
        for chunk in knowledge_context[:3]:  # Top 3 most relevant
            relevant_info.append(f"- {chunk['content'][:200]}...")
        
        prompt = f"""
Medical Case Analysis:

Patient Information:
- Age: {patient_history.get('age', 'Unknown')}
- Gender: {patient_history.get('gender', 'Unknown')}
- Medical History: {patient_history.get('medical_history', 'None reported')}
- Current Medications: {patient_history.get('medications', 'None reported')}

Current Symptoms:
{symptoms}

Relevant Medical Knowledge:
{chr(10).join(relevant_info)}

Please provide a brief medical assessment focusing on:
1. Most likely diagnosis
2. Key diagnostic considerations
3. Recommended immediate actions
"""
        return prompt
    
    def get_ai_diagnosis(self, symptoms: str, patient_history: Dict) -> Dict[str, Any]:
        """
        Generate AI-powered diagnosis using RAG and rule-based reasoning
        
        Args:
            symptoms (str): Patient symptoms description
            patient_history (Dict): Patient medical history and demographics
            
        Returns:
            Dict: Structured diagnosis with recommendations
        """
        try:
            # Step 1: Query knowledge base for relevant medical information
            knowledge_results = search_medical_knowledge(symptoms, top_k=5)
            
            # Step 2: Apply rule-based diagnostic matching
            rule_based_diagnoses = self._match_condition_rules(symptoms, patient_history)
            
            # Step 3: Calculate symptom severity
            severity_score = self._calculate_symptom_severity(symptoms)
            
            # Step 4: Get treatment recommendations for top diagnoses
            treatment_recommendations = []
            if rule_based_diagnoses:
                top_diagnosis = rule_based_diagnoses[0]['condition']
                treatment_results = get_treatment_recommendations(top_diagnosis, top_k=3)
                treatment_recommendations = [result['content'][:300] for result in treatment_results]
            
            # Step 5: Optional AI enhancement (if API key available)
            ai_insights = None
            if knowledge_results:
                prompt = self._format_medical_prompt(symptoms, patient_history, knowledge_results)
                ai_insights = self._query_huggingface_api(prompt)
            
            # Step 6: Determine urgency level
            urgency_level = self._determine_urgency(severity_score, rule_based_diagnoses)
            
            # Step 7: Format final diagnosis
            diagnosis_result = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_history.get('patient_id'),
                'symptoms_analyzed': symptoms,
                'severity_score': round(severity_score, 2),
                'urgency_level': urgency_level,
                'primary_diagnoses': rule_based_diagnoses[:self.max_diagnoses],
                'differential_diagnoses': [
                    {
                        'condition': 'Consider additional conditions based on symptoms',
                        'confidence': 0.3,
                        'note': 'Further diagnostic testing recommended'
                    }
                ] if not rule_based_diagnoses else [],
                'treatment_recommendations': treatment_recommendations,
                'knowledge_sources': len(knowledge_results),
                'ai_insights': ai_insights,
                'recommendations': self._generate_recommendations(
                    severity_score, rule_based_diagnoses, urgency_level
                ),
                'follow_up_required': urgency_level in ['critical', 'high'],
                'diagnostic_confidence': (
                    rule_based_diagnoses[0]['confidence'] if rule_based_diagnoses else 0.2
                )
            }
            
            return diagnosis_result
            
        except Exception as e:
            # Return error diagnosis
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f"Diagnostic analysis failed: {str(e)}",
                'symptoms_analyzed': symptoms,
                'urgency_level': 'unknown',
                'recommendations': ['Consult with healthcare provider immediately'],
                'diagnostic_confidence': 0.0
            }
    
    def _determine_urgency(self, severity_score: float, diagnoses: List[Dict]) -> str:
        """
        Determine urgency level based on severity and diagnoses
        
        Args:
            severity_score (float): Calculated severity score
            diagnoses (List[Dict]): Matched diagnoses
            
        Returns:
            str: Urgency level (critical, high, moderate, low)
        """
        # Check for critical conditions
        if diagnoses:
            top_urgency = diagnoses[0].get('urgency', 'low')
            if top_urgency == 'critical' or severity_score > 0.8:
                return 'critical'
            elif top_urgency == 'high' or severity_score > 0.6:
                return 'high'
            elif severity_score > 0.4:
                return 'moderate'
        
        return 'low' if severity_score <= 0.4 else 'moderate'
    
    def _generate_recommendations(self, severity_score: float, diagnoses: List[Dict], urgency: str) -> List[str]:
        """
        Generate clinical recommendations based on diagnosis
        
        Args:
            severity_score (float): Symptom severity score
            diagnoses (List[Dict]): Matched diagnoses
            urgency (str): Urgency level
            
        Returns:
            List[str]: Clinical recommendations
        """
        recommendations = []
        
        if urgency == 'critical':
            recommendations.extend([
                'Seek immediate emergency medical attention',
                'Consider calling 911 or visiting emergency department',
                'Monitor vital signs closely'
            ])
        elif urgency == 'high':
            recommendations.extend([
                'Schedule urgent appointment with healthcare provider',
                'Monitor symptoms closely for any worsening',
                'Consider same-day medical evaluation'
            ])
        elif urgency == 'moderate':
            recommendations.extend([
                'Schedule appointment with primary care provider within 24-48 hours',
                'Monitor symptoms and document any changes',
                'Consider symptomatic treatment as appropriate'
            ])
        else:
            recommendations.extend([
                'Monitor symptoms and consider routine medical follow-up',
                'Maintain symptom diary',
                'Schedule routine appointment if symptoms persist'
            ])
        
        # Add diagnosis-specific recommendations
        if diagnoses:
            top_diagnosis = diagnoses[0]['condition'].lower()
            if 'cardiac' in top_diagnosis or 'heart' in top_diagnosis:
                recommendations.append('Consider ECG and cardiac enzymes')
            elif 'respiratory' in top_diagnosis or 'pneumonia' in top_diagnosis:
                recommendations.append('Consider chest X-ray and oxygen saturation monitoring')
            elif 'infection' in top_diagnosis:
                recommendations.append('Consider complete blood count and cultures')
        
        return recommendations


# Global diagnostic engine instance
diagnostic_engine = MedicalAIDiagnosticEngine()


# Convenience function for easy integration
def get_ai_diagnosis(symptoms: str, patient_history: Dict) -> Dict[str, Any]:
    """
    Generate AI-powered medical diagnosis
    
    Args:
        symptoms (str): Patient symptoms description
        patient_history (Dict): Patient medical history and demographics
        
    Returns:
        Dict: Comprehensive diagnosis with treatment recommendations
    """
    return diagnostic_engine.get_ai_diagnosis(symptoms, patient_history)


def analyze_case_urgency(symptoms: str) -> str:
    """
    Quick urgency analysis for triage purposes
    
    Args:
        symptoms (str): Patient symptoms
        
    Returns:
        str: Urgency level
    """
    severity = diagnostic_engine._calculate_symptom_severity(symptoms)
    return diagnostic_engine._determine_urgency(severity, [])


def get_differential_diagnoses(symptoms: str, top_k: int = 5) -> List[Dict]:
    """
    Get list of potential diagnoses for given symptoms
    
    Args:
        symptoms (str): Patient symptoms
        top_k (int): Number of diagnoses to return
        
    Returns:
        List[Dict]: Potential diagnoses with confidence scores
    """
    patient_history = {'age': 0, 'gender': 'unknown'}  # Minimal history for screening
    matches = diagnostic_engine._match_condition_rules(symptoms, patient_history)
    return matches[:top_k]