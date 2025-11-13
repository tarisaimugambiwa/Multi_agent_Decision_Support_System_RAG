"""
AI Diagnosis utilities for Alera Healthcare System
Provides intelligent diagnostic suggestions using RAG and rule-based reasoning
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests
from django.conf import settings

from knowledge.rag_utils import search_medical_knowledge, get_treatment_recommendations, get_diagnostic_guidelines


# Diagnosis Prompt Template
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
6. Explain the diagnosis in simple language that a nurse can understand and explain to the patient

Format your response as structured JSON with the following fields:
- primary_diagnosis: The most likely condition (medical term)
- diagnosis_explanation: A clear, simple explanation of what this condition means, what causes it, and why you think the patient has it. Write this in plain language that anyone can understand, avoiding medical jargon.
- differential_diagnoses: List of other possible conditions
- treatment_plan: Recommended treatments and medications
- red_flags: Any warning signs requiring immediate attention
- follow_up_recommendations: Next steps and follow-up care
- confidence_score: Your confidence in this assessment (0-100)
- reasoning: Brief explanation of your diagnostic reasoning
"""


class MedicalAIDiagnosticEngine:
    """
    AI-powered diagnostic engine combining RAG with rule-based reasoning
    """
    
    def __init__(self):
        self.confidence_threshold = 0.4  # Lowered from 0.6 for better sensitivity
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
        
        # Common conditions with diagnostic criteria - Expanded for comprehensive diagnosis
        self.condition_rules = {
            # Cardiovascular
            'acute_coronary_syndrome': {
                'required_symptoms': ['chest pain'],
                'supporting_symptoms': ['shortness of breath', 'sweating', 'nausea', 'radiating pain'],
                'risk_factors': ['diabetes', 'hypertension', 'smoking', 'family history'],
                'urgency': 'critical',
                'confidence_boost': 0.3
            },
            'hypertensive_crisis': {
                'required_symptoms': ['headache', 'high blood pressure'],
                'supporting_symptoms': ['dizziness', 'chest pain', 'shortness of breath', 'blurred vision'],
                'risk_factors': ['hypertension', 'medication non-compliance'],
                'urgency': 'critical',
                'confidence_boost': 0.25
            },
            
            # Infectious Diseases - Common in Sub-Saharan Africa
            'malaria': {
                'required_symptoms': ['fever', 'chills'],
                'supporting_symptoms': ['headache', 'body aches', 'sweating', 'nausea', 'vomiting', 'fatigue'],
                'risk_factors': ['endemic area', 'travel', 'no prophylaxis', 'mosquito exposure'],
                'urgency': 'high',
                'confidence_boost': 0.25
            },
            'typhoid_fever': {
                'required_symptoms': ['fever', 'headache'],
                'supporting_symptoms': ['abdominal pain', 'weakness', 'loss of appetite', 'constipation', 'diarrhea'],
                'risk_factors': ['poor sanitation', 'contaminated food', 'contaminated water'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'tuberculosis': {
                'required_symptoms': ['cough', 'fever'],
                'supporting_symptoms': ['night sweats', 'weight loss', 'fatigue', 'chest pain', 'blood in sputum'],
                'risk_factors': ['hiv', 'immunocompromised', 'contact with tb', 'crowded living'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'hiv_related_illness': {
                'required_symptoms': ['fever', 'weight loss'],
                'supporting_symptoms': ['diarrhea', 'cough', 'fatigue', 'night sweats', 'enlarged lymph nodes'],
                'risk_factors': ['hiv positive', 'immunosuppressed', 'opportunistic infections'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'acute_febrile_illness': {
                'required_symptoms': ['fever'],
                'supporting_symptoms': ['headache', 'body aches', 'fatigue', 'chills', 'weakness', 'sweating'],
                'risk_factors': ['recent infection', 'exposure', 'travel', 'season'],
                'urgency': 'moderate',
                'confidence_boost': 0.2
            },
            
            # Respiratory Conditions
            'pneumonia': {
                'required_symptoms': ['cough', 'fever'],
                'supporting_symptoms': ['shortness of breath', 'chest pain', 'sputum', 'difficulty breathing'],
                'risk_factors': ['age', 'immunocompromised', 'chronic disease', 'smoking'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'upper_respiratory_infection': {
                'required_symptoms': ['cough'],
                'supporting_symptoms': ['fever', 'sore throat', 'runny nose', 'congestion', 'fatigue', 'headache'],
                'risk_factors': ['recent exposure', 'season', 'school', 'daycare'],
                'urgency': 'low',
                'confidence_boost': 0.15
            },
            'bronchitis': {
                'required_symptoms': ['cough'],
                'supporting_symptoms': ['sputum', 'chest discomfort', 'fever', 'fatigue', 'shortness of breath'],
                'risk_factors': ['smoking', 'recent infection', 'season'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            'asthma_exacerbation': {
                'required_symptoms': ['shortness of breath', 'wheezing'],
                'supporting_symptoms': ['cough', 'chest tightness', 'difficulty breathing', 'anxiety'],
                'risk_factors': ['asthma history', 'allergies', 'triggers', 'season'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            
            # Gastrointestinal Conditions
            'gastroenteritis': {
                'required_symptoms': ['diarrhea'],
                'supporting_symptoms': ['nausea', 'vomiting', 'abdominal pain', 'fever', 'dehydration'],
                'risk_factors': ['recent travel', 'food poisoning', 'contact', 'contaminated water'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            'appendicitis': {
                'required_symptoms': ['abdominal pain'],
                'supporting_symptoms': ['nausea', 'vomiting', 'fever', 'loss of appetite', 'right lower quadrant pain'],
                'risk_factors': ['age', 'sudden onset'],
                'urgency': 'critical',
                'confidence_boost': 0.2
            },
            'peptic_ulcer': {
                'required_symptoms': ['abdominal pain'],
                'supporting_symptoms': ['nausea', 'vomiting', 'bloating', 'heartburn', 'blood in stool'],
                'risk_factors': ['h pylori', 'nsaid use', 'stress', 'smoking'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            
            # Pediatric Conditions
            'measles': {
                'required_symptoms': ['fever', 'rash'],
                'supporting_symptoms': ['cough', 'runny nose', 'red eyes', 'white spots in mouth'],
                'risk_factors': ['unvaccinated', 'exposure', 'outbreak'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            'chickenpox': {
                'required_symptoms': ['rash', 'fever'],
                'supporting_symptoms': ['itching', 'blisters', 'fatigue', 'loss of appetite'],
                'risk_factors': ['unvaccinated', 'exposure', 'school age'],
                'urgency': 'moderate',
                'confidence_boost': 0.2
            },
            'acute_diarrheal_disease': {
                'required_symptoms': ['diarrhea'],
                'supporting_symptoms': ['vomiting', 'fever', 'abdominal cramps', 'dehydration'],
                'risk_factors': ['children', 'contaminated water', 'poor sanitation'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            'malnutrition': {
                'required_symptoms': ['weight loss', 'weakness'],
                'supporting_symptoms': ['fatigue', 'edema', 'hair loss', 'skin changes', 'irritability'],
                'risk_factors': ['poverty', 'food insecurity', 'chronic disease'],
                'urgency': 'high',
                'confidence_boost': 0.15
            },
            
            # Metabolic/Endocrine
            'diabetes_mellitus': {
                'required_symptoms': ['excessive thirst', 'frequent urination'],
                'supporting_symptoms': ['weight loss', 'fatigue', 'blurred vision', 'hunger'],
                'risk_factors': ['family history', 'obesity', 'sedentary lifestyle'],
                'urgency': 'moderate',
                'confidence_boost': 0.2
            },
            'diabetic_ketoacidosis': {
                'required_symptoms': ['nausea', 'vomiting', 'abdominal pain'],
                'supporting_symptoms': ['confusion', 'rapid breathing', 'fruity breath', 'excessive thirst'],
                'risk_factors': ['diabetes', 'infection', 'medication non-compliance'],
                'urgency': 'critical',
                'confidence_boost': 0.25
            },
            
            # Neurological
            'migraine': {
                'required_symptoms': ['headache'],
                'supporting_symptoms': ['nausea', 'light sensitivity', 'sound sensitivity', 'visual disturbances'],
                'risk_factors': ['family history', 'stress', 'hormonal changes', 'triggers'],
                'urgency': 'low',
                'confidence_boost': 0.1
            },
            'meningitis': {
                'required_symptoms': ['severe headache', 'fever', 'neck stiffness'],
                'supporting_symptoms': ['confusion', 'sensitivity to light', 'nausea', 'vomiting'],
                'risk_factors': ['recent infection', 'immunocompromised', 'close contact'],
                'urgency': 'critical',
                'confidence_boost': 0.3
            },
            'stroke': {
                'required_symptoms': ['weakness', 'confusion'],
                'supporting_symptoms': ['slurred speech', 'facial drooping', 'numbness', 'vision changes'],
                'risk_factors': ['hypertension', 'diabetes', 'smoking', 'age'],
                'urgency': 'critical',
                'confidence_boost': 0.3
            },
            'seizure_disorder': {
                'required_symptoms': ['seizure'],
                'supporting_symptoms': ['loss of consciousness', 'confusion', 'muscle spasms', 'headache'],
                'risk_factors': ['epilepsy', 'head injury', 'fever', 'medication'],
                'urgency': 'high',
                'confidence_boost': 0.2
            },
            
            # Other Common Conditions
            'anemia': {
                'required_symptoms': ['fatigue', 'weakness'],
                'supporting_symptoms': ['pale skin', 'dizziness', 'shortness of breath', 'cold hands'],
                'risk_factors': ['poor nutrition', 'bleeding', 'chronic disease', 'pregnancy'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            'urinary_tract_infection': {
                'required_symptoms': ['frequent urination', 'burning sensation'],
                'supporting_symptoms': ['cloudy urine', 'blood in urine', 'pelvic pain', 'fever'],
                'risk_factors': ['female', 'sexual activity', 'poor hygiene'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
            },
            'coeliac_disease': {
                'required_symptoms': ['abdominal pain', 'diarrhea'],
                'supporting_symptoms': ['bloating', 'weight loss', 'fatigue', 'nausea', 'constipation'],
                'risk_factors': ['family history', 'gluten exposure', 'autoimmune'],
                'urgency': 'low',
                'confidence_boost': 0.15
            },
            'dehydration': {
                'required_symptoms': ['thirst', 'dry mouth'],
                'supporting_symptoms': ['dizziness', 'weakness', 'dark urine', 'fatigue', 'confusion'],
                'risk_factors': ['diarrhea', 'vomiting', 'fever', 'excessive sweating'],
                'urgency': 'moderate',
                'confidence_boost': 0.15
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
            
            # Check required symptoms - use flexible matching
            required_count = 0
            for symptom in rules['required_symptoms']:
                # Check for partial matches (e.g., "fever" matches "high fever", "febrile")
                symptom_words = symptom.split()
                if any(word in symptoms_lower for word in symptom_words):
                    required_count += 1
            
            # Require at least one required symptom
            if required_count == 0:
                continue
            
            # Scale confidence based on how many required symptoms matched
            required_ratio = required_count / len(rules['required_symptoms'])
            confidence += 0.4 * required_ratio  # Base confidence
            
            # Check supporting symptoms
            supporting_count = sum(1 for symptom in rules['supporting_symptoms'] 
                                 if any(word in symptoms_lower for word in symptom.split()))
            supporting_ratio = supporting_count / len(rules['supporting_symptoms']) if rules['supporting_symptoms'] else 0
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
    
    def _query_ollama_api(self, prompt: str) -> Optional[Dict]:
        """
        Query Ollama local LLM for AI-powered diagnosis with reasoning
        
        Args:
            prompt (str): Medical prompt for analysis
            
        Returns:
            Optional[Dict]: Parsed AI response with diagnosis details or None if unavailable
        """
        try:
            # Ollama API endpoint (default local installation)
            ollama_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434/api/generate')
            ollama_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')  # or 'mistral', 'meditron', etc.
            
            payload = {
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Request JSON output
            }
            
            response = requests.post(ollama_url, json=payload, timeout=120)  # Reduced to 2 minutes
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Try to parse JSON response
                try:
                    diagnosis_data = json.loads(response_text)
                    return diagnosis_data
                except json.JSONDecodeError:
                    # If not valid JSON, return as text
                    return {'text_response': response_text}
            else:
                print(f"Ollama API error: {response.status_code}")
                return None
            
        except requests.exceptions.ConnectionError:
            print("Warning: Ollama not running. Install Ollama from https://ollama.ai/ and run 'ollama serve'")
            return None
        except Exception as e:
            print(f"Error querying Ollama API: {str(e)}")
            return None
    
    def _query_huggingface_api(self, prompt: str) -> Optional[str]:
        """
        Query Hugging Face API for additional AI insights (optional - fallback)
        
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
        Format a structured medical prompt for AI analysis using the DIAGNOSIS_PROMPT template
        
        Args:
            symptoms (str): Patient symptoms
            patient_history (Dict): Patient medical history
            knowledge_context (List[Dict]): Retrieved medical knowledge
            
        Returns:
            str: Formatted medical prompt
        """
        # Extract key information from knowledge context
        relevant_info = []
        for chunk in knowledge_context[:5]:  # Top 5 most relevant
            relevant_info.append(f"- {chunk['content'][:300]}...")
        
        # Extract vital signs if available
        vital_signs = patient_history.get('vital_signs', 'Not recorded')
        if isinstance(vital_signs, dict):
            vital_signs = ', '.join([f"{k}: {v}" for k, v in vital_signs.items()])
        
        # Use the DIAGNOSIS_PROMPT template and format with patient data
        prompt = DIAGNOSIS_PROMPT.format(
            age=patient_history.get('age', 'Unknown'),
            gender=patient_history.get('gender', 'Unknown'),
            symptoms=symptoms,
            vital_signs=vital_signs,
            medical_history=patient_history.get('medical_history', 'None reported'),
            retrieved_context='\n'.join(relevant_info)
        )
        
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
                # Extract symptoms list from symptoms string
                symptom_list = [s.strip() for s in symptoms.split(',')]
                treatment_results = get_treatment_recommendations(top_diagnosis, symptom_list, top_k=3)
                treatment_recommendations = [result['content'][:300] for result in treatment_results]
            
            # Step 5: AI-powered diagnosis with Ollama (using knowledge base context)
            ai_diagnosis = None
            ollama_confidence = None
            ollama_reasoning = None
            diagnosis_explanation = None
            
            if knowledge_results:
                prompt = self._format_medical_prompt(symptoms, patient_history, knowledge_results)
                
                # Try Ollama first (local LLM with reasoning)
                ai_response = self._query_ollama_api(prompt)
                
                if ai_response and isinstance(ai_response, dict):
                    # Extract structured diagnosis from Ollama
                    ai_diagnosis = ai_response.get('primary_diagnosis', ai_response.get('text_response', ''))
                    ollama_confidence = ai_response.get('confidence_score', 0) / 100.0  # Convert to 0-1 scale
                    ollama_reasoning = ai_response.get('reasoning', '')
                    
                    # Extract plain language explanation
                    diagnosis_explanation = ai_response.get('diagnosis_explanation', '')
                    
                    # Update differential diagnoses if provided by Ollama
                    if 'differential_diagnoses' in ai_response and ai_response['differential_diagnoses']:
                        ollama_differentials = ai_response['differential_diagnoses']
                        if isinstance(ollama_differentials, list):
                            # Merge with rule-based diagnoses
                            for diff in ollama_differentials[:3]:
                                if isinstance(diff, str):
                                    diff = {'condition': diff, 'confidence': 0.5}
                                rule_based_diagnoses.append({
                                    'condition': diff.get('condition', diff) if isinstance(diff, dict) else diff,
                                    'confidence': diff.get('confidence', 0.5) if isinstance(diff, dict) else 0.5,
                                    'reasoning': 'AI-suggested based on knowledge base',
                                    'urgency': 'moderate'
                                })
                    
                    # Extract treatment plan if provided
                    if 'treatment_plan' in ai_response and ai_response['treatment_plan']:
                        ai_treatment = ai_response['treatment_plan']
                        if isinstance(ai_treatment, str):
                            treatment_recommendations.insert(0, ai_treatment[:300])
                        elif isinstance(ai_treatment, list):
                            treatment_recommendations = ai_treatment[:3] + treatment_recommendations
                    
                    # Extract red flags if provided
                    ai_red_flags = ai_response.get('red_flags', [])
                    if ai_red_flags and isinstance(ai_red_flags, list):
                        # Store for later use
                        pass
                
                # Fallback to HuggingFace if Ollama unavailable
                if not ai_diagnosis:
                    ai_insights = self._query_huggingface_api(prompt)
                    if ai_insights:
                        ai_diagnosis = ai_insights
            
            # Boost confidence if Ollama agrees with rule-based diagnosis
            if rule_based_diagnoses and ai_diagnosis and ollama_confidence:
                top_rule_diagnosis = rule_based_diagnoses[0]['condition'].lower()
                if isinstance(ai_diagnosis, str) and top_rule_diagnosis in ai_diagnosis.lower():
                    # Ollama agrees - boost confidence
                    rule_based_diagnoses[0]['confidence'] = min(
                        rule_based_diagnoses[0]['confidence'] + 0.2,
                        0.98
                    )
                    rule_based_diagnoses[0]['ai_confirmed'] = True
            
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
                'ai_diagnosis': ai_diagnosis,  # Ollama's diagnosis
                'ai_reasoning': ollama_reasoning,  # Ollama's reasoning
                'ai_confidence': ollama_confidence,  # Ollama's confidence
                'diagnosis_explanation': diagnosis_explanation,  # Plain language explanation for nurses
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