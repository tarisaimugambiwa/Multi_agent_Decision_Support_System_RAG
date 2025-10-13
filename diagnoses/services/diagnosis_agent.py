"""
DIAGNOSIS AGENT - 🤖 AI-Powered Symptom Analysis

RESPONSIBILITIES:
- Analyze symptom patterns using AI
- Generate differential diagnoses with confidence scores
- Consider patient medical history and demographics
- Identify red flags and emergency conditions
- Provide diagnostic reasoning and explanations
"""

import logging
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DiagnosisAgent:
    """
    Diagnosis Agent analyzes symptoms and generates differential diagnoses using AI.
    Uses both pattern recognition and AI language models.
    """
    
    # Red flag symptoms requiring immediate attention
    RED_FLAGS = {
        'cardiac': ['chest pain', 'chest pressure', 'crushing pain', 'radiating pain to arm'],
        'neurological': ['severe headache', 'confusion', 'loss of consciousness', 'slurred speech', 'weakness one side'],
        'respiratory': ['severe difficulty breathing', 'unable to speak', 'blue lips', 'gasping'],
        'abdominal': ['severe abdominal pain', 'rigid abdomen', 'vomiting blood', 'blood in stool'],
        'trauma': ['severe bleeding', 'compound fracture', 'head injury with confusion'],
        'allergic': ['severe allergic reaction', 'swelling throat', 'difficulty swallowing', 'hives with breathing difficulty']
    }
    
    def __init__(self):
        """Initialize the Diagnosis Agent."""
        self.name = "Diagnosis Agent"
        self.ai_model = None
        self._initialize_ai_model()
        logger.info(f"{self.name} initialized")
    
    def _initialize_ai_model(self):
        """Initialize AI model for diagnosis generation."""
        try:
            from diagnoses.ai_utils import get_ai_diagnosis
            self.ai_model = get_ai_diagnosis
            logger.info("AI diagnosis model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            self.ai_model = None
    
    def analyze_symptoms(
        self,
        symptoms: str,
        patient_history: Dict = None,
        demographics: Dict = None,
        vital_signs: Dict = None,
        retriever_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Analyze symptoms and generate differential diagnoses.
        
        Args:
            symptoms: Patient symptoms description
            patient_history: Patient medical history
            demographics: Patient age, gender, etc.
            vital_signs: Current vital signs
            retriever_context: Context from RetrieverAgent
            
        Returns:
            Dict containing diagnosis analysis with confidence scores
        """
        logger.info(f"Analyzing symptoms: '{symptoms[:50]}...'")
        
        # Identify red flags
        red_flags = self._identify_red_flags(symptoms)
        
        # Check for emergency conditions
        emergency_conditions = self._detect_emergency_conditions(symptoms, vital_signs)
        
        # Build comprehensive patient context
        patient_context = self._build_patient_context(
            patient_history, demographics, vital_signs
        )
        
        # Generate AI diagnosis
        ai_diagnosis = self._generate_ai_diagnosis(
            symptoms, patient_context, retriever_context
        )
        
        # Generate differential diagnoses
        differential_diagnoses = self._generate_differential_diagnoses(
            symptoms, patient_context, ai_diagnosis
        )
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence_score(
            ai_diagnosis, differential_diagnoses, red_flags
        )
        
        # Create comprehensive analysis
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'primary_diagnosis': ai_diagnosis.get('diagnosis', 'Unable to determine'),
            'explanation': ai_diagnosis.get('explanation', ''),  # Plain language explanation
            'confidence_score': confidence_score,
            'differential_diagnoses': differential_diagnoses,
            'red_flags': red_flags,
            'emergency_conditions': emergency_conditions,
            'urgency_assessment': self._assess_urgency_level(red_flags, emergency_conditions),
            'diagnostic_reasoning': ai_diagnosis.get('reasoning', ''),
            'recommended_tests': self._recommend_diagnostic_tests(differential_diagnoses),
            'clinical_notes': self._generate_clinical_notes(symptoms, ai_diagnosis),
            'ai_raw_response': ai_diagnosis,
        }
        
        logger.info(f"Diagnosis analysis completed. Primary: {analysis['primary_diagnosis']}, Confidence: {confidence_score:.2f}")
        
        return analysis
    
    def _identify_red_flags(self, symptoms: str) -> List[Dict[str, str]]:
        """
        Identify red flag symptoms requiring immediate attention.
        
        Returns:
            List of red flags with category and description
        """
        symptoms_lower = symptoms.lower()
        identified_flags = []
        
        for category, flag_list in self.RED_FLAGS.items():
            for flag in flag_list:
                if flag in symptoms_lower:
                    identified_flags.append({
                        'category': category,
                        'flag': flag,
                        'severity': 'HIGH',
                        'action': 'IMMEDIATE MEDICAL ATTENTION REQUIRED'
                    })
        
        return identified_flags
    
    def _detect_emergency_conditions(self, symptoms: str, vital_signs: Dict = None) -> List[str]:
        """
        Detect potential emergency conditions.
        
        Returns:
            List of potential emergency conditions
        """
        emergencies = []
        symptoms_lower = symptoms.lower()
        
        # Cardiac emergencies
        cardiac_indicators = ['chest pain', 'heart attack', 'cardiac arrest', 'crushing chest pain']
        if any(indicator in symptoms_lower for indicator in cardiac_indicators):
            emergencies.append('CARDIAC EMERGENCY')
        
        # Stroke indicators
        stroke_indicators = ['stroke', 'facial drooping', 'arm weakness', 'speech difficulty']
        if any(indicator in symptoms_lower for indicator in stroke_indicators):
            emergencies.append('STROKE')
        
        # Respiratory distress
        respiratory_indicators = ['cannot breathe', 'severe breathing difficulty', 'turning blue']
        if any(indicator in symptoms_lower for indicator in respiratory_indicators):
            emergencies.append('RESPIRATORY DISTRESS')
        
        # Severe bleeding
        if 'severe bleeding' in symptoms_lower or 'uncontrolled bleeding' in symptoms_lower:
            emergencies.append('SEVERE HEMORRHAGE')
        
        # Anaphylaxis
        anaphylaxis_indicators = ['anaphylaxis', 'severe allergic reaction', 'throat swelling']
        if any(indicator in symptoms_lower for indicator in anaphylaxis_indicators):
            emergencies.append('ANAPHYLAXIS')
        
        # Check vital signs for emergency indicators
        if vital_signs:
            if vital_signs.get('oxygen_saturation') and int(vital_signs['oxygen_saturation']) < 90:
                emergencies.append('HYPOXEMIA')
            
            if vital_signs.get('temperature') and float(vital_signs['temperature']) > 103:
                emergencies.append('HYPERTHERMIA')
        
        return emergencies
    
    def _build_patient_context(
        self,
        patient_history: Dict = None,
        demographics: Dict = None,
        vital_signs: Dict = None
    ) -> str:
        """
        Build comprehensive patient context for AI diagnosis.
        
        Returns:
            Formatted patient context string
        """
        context_parts = []
        
        if demographics:
            age = demographics.get('age', 'unknown')
            gender = demographics.get('gender', 'unknown')
            context_parts.append(f"Patient: {age} year old {gender}")
        
        if patient_history:
            medical_history = patient_history.get('medical_history', '')
            if medical_history:
                context_parts.append(f"Medical History: {medical_history}")
            
            allergies = patient_history.get('allergies', '')
            if allergies:
                context_parts.append(f"Allergies: {allergies}")
        
        if vital_signs:
            vital_str = ", ".join([f"{k}: {v}" for k, v in vital_signs.items()])
            context_parts.append(f"Vital Signs: {vital_str}")
        
        return "\n".join(context_parts) if context_parts else "No additional patient context available"
    
    def _generate_ai_diagnosis(
        self,
        symptoms: str,
        patient_context: str,
        retriever_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered diagnosis using LLM with RAG context from medical documents.
        
        Returns:
            Dict containing AI diagnosis with evidence from loaded documents
        """
        if not self.ai_model:
            logger.warning("AI model not available, using fallback diagnosis")
            return {
                'diagnosis': 'Unable to generate AI diagnosis - model not available',
                'reasoning': 'AI model not initialized',
                'confidence': 0.5
            }
        
        try:
            # Build enhanced context with RAG results
            enhanced_context = patient_context
            
            if retriever_context and retriever_context.get('results'):
                # Add medical knowledge from loaded documents
                enhanced_context += "\n\n--- MEDICAL KNOWLEDGE BASE REFERENCES ---\n"
                for idx, result in enumerate(retriever_context['results'][:3], 1):
                    source = result.get('source', 'Unknown')
                    content = result.get('content', '')[:500]  # Limit to 500 chars per excerpt
                    enhanced_context += f"\n[Reference {idx} from {source}]:\n{content}\n"
                
                enhanced_context += f"\n\nBased on {len(retriever_context['results'])} medical guidelines, "
                enhanced_context += f"from sources: {', '.join(retriever_context.get('sources', [])[:3])}"
            
            # Build patient history dict for AI model
            patient_history_dict = {
                'medical_history': enhanced_context,
                'age': 'unknown',
                'gender': 'unknown'
            }
            
            # Call AI diagnosis engine with enhanced context
            ai_result = self.ai_model(symptoms, patient_history_dict)
            
            # Parse the result from diagnostic engine
            if isinstance(ai_result, dict):
                # Extract primary diagnosis from diagnostic engine results
                primary_diagnoses = ai_result.get('primary_diagnoses', [])
                
                # Extract plain language explanation
                diagnosis_explanation = ai_result.get('diagnosis_explanation', '')
                
                if primary_diagnoses and len(primary_diagnoses) > 0:
                    top_diagnosis = primary_diagnoses[0]
                    diagnosis_name = top_diagnosis.get('condition', 'Unknown condition')
                    diagnosis_confidence = top_diagnosis.get('confidence', 0.5)
                    
                    # Get treatment recommendations
                    treatment_recs = ai_result.get('treatment_recommendations', [])
                    reasoning = f"Based on symptom analysis and medical guidelines. "
                    if treatment_recs:
                        reasoning += f"Treatment guidelines available. "
                    
                    # Add knowledge base sources
                    reasoning += f"Analysis used {ai_result.get('knowledge_sources', 0)} medical references."
                else:
                    # Fallback if no diagnoses matched
                    diagnosis_name = 'Unable to determine specific diagnosis'
                    diagnosis_confidence = 0.3
                    reasoning = 'Symptoms do not match clear diagnostic patterns. Further evaluation recommended.'
                
                return {
                    'diagnosis': diagnosis_name,
                    'confidence': diagnosis_confidence,
                    'reasoning': reasoning,
                    'explanation': diagnosis_explanation,  # Plain language explanation
                    'urgency_level': ai_result.get('urgency_level', 'moderate'),
                    'severity_score': ai_result.get('severity_score', 0.5),
                    'rag_sources': retriever_context.get('sources', []) if retriever_context else [],
                    'knowledge_base_used': retriever_context.get('knowledge_base_used', False) if retriever_context else False,
                    'ai_raw_response': ai_result
                }
            else:
                return {
                    'diagnosis': str(ai_result),
                    'reasoning': 'AI diagnosis generated',
                    'confidence': 0.6,
                    'explanation': '',  # No explanation available
                    'rag_sources': retriever_context.get('sources', []) if retriever_context else [],
                    'knowledge_base_used': retriever_context.get('knowledge_base_used', False) if retriever_context else False
                }
        
        except Exception as e:
            logger.error(f"Error generating AI diagnosis with RAG: {e}")
            return {
                'diagnosis': 'Error generating diagnosis',
                'reasoning': str(e),
                'confidence': 0.0,
                'error': True,
                'rag_sources': [],
                'knowledge_base_used': False
            }
    
    def _generate_differential_diagnoses(
        self,
        symptoms: str,
        patient_context: str,
        ai_diagnosis: Dict
    ) -> List[Dict[str, Any]]:
        """
        Generate differential diagnoses with confidence scores.
        
        Returns:
            List of differential diagnoses
        """
        differentials = []
        
        # Add AI primary diagnosis as top differential
        primary = ai_diagnosis.get('diagnosis', '')
        if primary:
            differentials.append({
                'diagnosis': primary,
                'confidence': ai_diagnosis.get('confidence', 0.7),
                'likelihood': 'HIGH',
                'reasoning': ai_diagnosis.get('reasoning', '')
            })
        
        # Add rule-based differentials based on symptom patterns
        symptom_patterns = self._analyze_symptom_patterns(symptoms)
        
        for pattern in symptom_patterns:
            if pattern not in [d['diagnosis'] for d in differentials]:
                differentials.append({
                    'diagnosis': pattern['condition'],
                    'confidence': pattern['confidence'],
                    'likelihood': pattern['likelihood'],
                    'reasoning': pattern['reasoning']
                })
        
        # Sort by confidence
        differentials.sort(key=lambda x: x['confidence'], reverse=True)
        
        return differentials[:5]  # Return top 5
    
    def _analyze_symptom_patterns(self, symptoms: str) -> List[Dict]:
        """
        Analyze symptom patterns for rule-based diagnosis suggestions.
        
        Returns:
            List of potential diagnoses based on patterns
        """
        patterns = []
        symptoms_lower = symptoms.lower()
        
        # Respiratory infections
        if any(s in symptoms_lower for s in ['cough', 'fever', 'sore throat']):
            patterns.append({
                'condition': 'Upper Respiratory Infection',
                'confidence': 0.65,
                'likelihood': 'MODERATE',
                'reasoning': 'Classic symptoms of URI present'
            })
        
        # Influenza
        if all(s in symptoms_lower for s in ['fever', 'body aches', 'fatigue']):
            patterns.append({
                'condition': 'Influenza',
                'confidence': 0.70,
                'likelihood': 'HIGH',
                'reasoning': 'Symptom triad consistent with flu'
            })
        
        # Gastroenteritis
        if any(s in symptoms_lower for s in ['vomiting', 'diarrhea', 'nausea']):
            patterns.append({
                'condition': 'Gastroenteritis',
                'confidence': 0.68,
                'likelihood': 'MODERATE',
                'reasoning': 'GI symptoms present'
            })
        
        # Migraine
        if 'headache' in symptoms_lower and any(s in symptoms_lower for s in ['nausea', 'light sensitivity', 'aura']):
            patterns.append({
                'condition': 'Migraine',
                'confidence': 0.72,
                'likelihood': 'HIGH',
                'reasoning': 'Headache with associated symptoms'
            })
        
        return patterns
    
    def _calculate_confidence_score(
        self,
        ai_diagnosis: Dict,
        differential_diagnoses: List[Dict],
        red_flags: List[Dict]
    ) -> float:
        """
        Calculate overall confidence score for diagnosis.
        
        Returns:
            Confidence score between 0 and 1
        """
        # Start with AI confidence
        base_confidence = ai_diagnosis.get('confidence', 0.5)
        
        # Reduce confidence if red flags present (more uncertainty)
        if red_flags:
            base_confidence *= 0.9
        
        # Adjust based on number of differentials (more = less certainty)
        if len(differential_diagnoses) > 3:
            base_confidence *= 0.95
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _assess_urgency_level(self, red_flags: List, emergency_conditions: List) -> str:
        """
        Assess urgency level based on red flags and emergency conditions.
        
        Returns:
            Urgency level string
        """
        if emergency_conditions:
            return 'CRITICAL'
        elif red_flags:
            return 'HIGH'
        else:
            return 'ROUTINE'
    
    def _recommend_diagnostic_tests(self, differential_diagnoses: List[Dict]) -> List[str]:
        """
        Recommend diagnostic tests based on differential diagnoses.
        
        Returns:
            List of recommended tests
        """
        tests = []
        
        for diff in differential_diagnoses[:3]:  # Top 3 differentials
            diagnosis = diff['diagnosis'].lower()
            
            if 'infection' in diagnosis or 'fever' in diagnosis:
                tests.extend(['Complete Blood Count (CBC)', 'Blood Culture'])
            
            if 'cardiac' in diagnosis or 'heart' in diagnosis:
                tests.extend(['ECG', 'Cardiac Enzymes', 'Chest X-ray'])
            
            if 'respiratory' in diagnosis or 'pneumonia' in diagnosis:
                tests.extend(['Chest X-ray', 'Pulse Oximetry'])
            
            if 'gastro' in diagnosis:
                tests.extend(['Stool Analysis', 'Electrolyte Panel'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tests = []
        for test in tests:
            if test not in seen:
                seen.add(test)
                unique_tests.append(test)
        
        return unique_tests[:5]  # Return top 5 tests
    
    def _generate_clinical_notes(self, symptoms: str, ai_diagnosis: Dict) -> str:
        """
        Generate clinical notes for the diagnosis.
        
        Returns:
            Formatted clinical notes
        """
        notes = f"## Clinical Assessment\n\n"
        notes += f"**Presenting Symptoms:** {symptoms[:200]}...\n\n"
        notes += f"**AI Diagnosis:** {ai_diagnosis.get('diagnosis', 'Unknown')}\n\n"
        
        reasoning = ai_diagnosis.get('reasoning', '')
        if reasoning:
            notes += f"**Clinical Reasoning:** {reasoning}\n\n"
        
        return notes
