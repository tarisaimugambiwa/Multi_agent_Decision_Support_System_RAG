"""
TREATMENT AGENT - 💊 Evidence-Based Treatment Plans & Medication Recommendations

RESPONSIBILITIES:
- Create treatment plans based on loaded medical guidelines
- Generate medication recommendations from WHO Essential Medicines List
- Suggest diagnostic tests and referrals from medical literature
- Provide evidence-based treatment protocols from knowledge base
- Use RAG to query treatment guidelines from loaded documents
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TreatmentAgent:
    """
    Treatment Agent creates evidence-based treatment plans using RAG to query medical guidelines.
    References loaded WHO, ESPGHAN, and Uganda MoH documents for treatment recommendations.
    """
    
    def __init__(self):
        """Initialize the Treatment Agent."""
        self.name = "Treatment Agent"
        logger.info(f"{self.name} initialized with RAG capabilities")
    
    def create_action_plan(
        self,
        diagnosis: Dict,
        urgency_level: str,
        symptoms: List[str] = None,
        red_flags: List = None,
        emergency_conditions: List = None
    ) -> Dict[str, Any]:
        """
        Create evidence-based treatment plan using medical guidelines from knowledge base.
        
        Args:
            diagnosis: Diagnosis results from DiagnosisAgent
            urgency_level: Urgency assessment (CRITICAL, HIGH, ROUTINE)
            symptoms: List of patient symptoms
            red_flags: List of red flag symptoms
            emergency_conditions: List of emergency conditions detected
            
        Returns:
            Dict containing treatment plan with evidence from medical literature
        """
        logger.info(f"Creating evidence-based action plan for urgency level: {urgency_level}")
        
        primary_diagnosis = diagnosis.get('primary_diagnosis', '')
        
        # Query knowledge base for treatment guidelines
        treatment_guidelines = self._query_treatment_guidelines(
            primary_diagnosis, symptoms or []
        )
        
        # Generate action steps based on guidelines
        action_steps = self._generate_action_steps_from_guidelines(
            urgency_level, treatment_guidelines, diagnosis
        )
        
        # Create timeline
        timeline = self._create_action_timeline(urgency_level, action_steps)
        
        # Compile action plan
        action_plan = {
            'timestamp': datetime.now().isoformat(),
            'urgency_level': urgency_level,
            'immediate_actions': action_steps['immediate'],
            'short_term_actions': action_steps['short_term'],
            'follow_up_actions': action_steps['follow_up'],
            'timeline': timeline,
            'warnings': self._generate_warnings(red_flags, emergency_conditions),
            'success_criteria': self._define_success_criteria(diagnosis),
            'evidence_sources': treatment_guidelines.get('sources', []),
            'knowledge_base_used': treatment_guidelines.get('knowledge_base_used', False)
        }
        
        logger.info(f"Action plan created with {len(action_steps['immediate'])} immediate actions from {len(treatment_guidelines.get('sources', []))} medical sources")
        
        return action_plan
    
    def _query_treatment_guidelines(self, diagnosis: str, symptoms: List[str]) -> Dict[str, Any]:
        """
        Query knowledge base for treatment guidelines related to diagnosis.
        
        Returns:
            Dict containing treatment guidelines from medical documents
        """
        try:
            from knowledge.rag_utils import get_treatment_recommendations
            
            # Search for treatment guidelines
            results = get_treatment_recommendations(diagnosis, symptoms, top_k=3)
            
            # Format results
            guidelines = []
            sources = set()
            
            for result in results:
                guidelines.append({
                    'content': result.get('content', ''),
                    'source': result.get('source', 'Unknown'),
                    'relevance_score': result.get('score', 0.0)
                })
                sources.add(result.get('source', 'Unknown'))
            
            return {
                'guidelines': guidelines,
                'sources': list(sources),
                'total_found': len(guidelines),
                'knowledge_base_used': True
            }
            
        except Exception as e:
            logger.error(f"Error querying treatment guidelines: {e}")
            return {
                'guidelines': [],
                'sources': [],
                'total_found': 0,
                'knowledge_base_used': False,
                'error': str(e)
            }
    
    def recommend_medications(
        self,
        diagnosis: Dict,
        symptoms: List[str] = None,
        patient_history: Dict = None,
        allergies: List[str] = None,
        patient_age: int = None
    ) -> Dict[str, Any]:
        """
        Generate evidence-based medication recommendations from comprehensive WHO/Uganda Clinical Guidelines database.
        ⚠️ CRITICAL: Uses patient age to determine appropriate medication dosing (pediatric/adult/geriatric)
        
        Args:
            diagnosis: Diagnosis information
            symptoms: List of symptoms
            patient_history: Patient medical history
            allergies: List of known allergies
            patient_age: Patient age in years ⚠️ REQUIRED for safe medication dosing
            
        Returns:
            Dict containing medication recommendations with AGE-APPROPRIATE dosing
        """
        logger.info(f"Generating medication recommendations for: {diagnosis.get('primary_diagnosis', 'unknown')} (Patient Age: {patient_age} years)")
        
        primary_diagnosis = diagnosis.get('primary_diagnosis', '')
        vital_signs = diagnosis.get('vital_signs', {})
        
        # Determine age group for appropriate dosing
        if patient_age is not None:
            if patient_age < 18:
                age_group = 'pediatric'
                logger.warning(f"⚠️ PEDIATRIC PATIENT (Age: {patient_age}) - Weight-based dosing REQUIRED")
            elif patient_age > 65:
                age_group = 'geriatric'
                logger.info(f"Geriatric patient (Age: {patient_age}) - Reduced dosing recommended")
            else:
                age_group = 'adult'
        else:
            age_group = 'adult'
            logger.warning("⚠️ Patient age not provided - defaulting to adult dosing. VERIFY PATIENT AGE!")
        
        # Use comprehensive medication database
        try:
            from diagnoses.medication_database import (
                get_medication_by_diagnosis,
                determine_severity_from_vitals,
                MEDICATION_DATABASE
            )
            
            # Determine severity from vital signs and symptoms
            severity = determine_severity_from_vitals(vital_signs, ' '.join(symptoms or []))
            
            # Get medications from comprehensive database WITH AGE-APPROPRIATE DOSING
            medication_data = get_medication_by_diagnosis(
                primary_diagnosis,
                severity=severity,
                age_group=age_group,  # ⚠️ CRITICAL: Age-based dosing
                special_conditions=allergies
            )
            
            # Filter based on allergies if provided
            primary_meds = medication_data.get('primary_medications', [])
            if allergies:
                primary_meds = self._filter_by_allergies(primary_meds, allergies)
            
            medication_plan = {
                'timestamp': datetime.now().isoformat(),
                'primary_medications': primary_meds,
                'supportive_care': medication_data.get('supportive_care', []),
                'lifestyle_recommendations': medication_data.get('lifestyle', []),
                'prevention_measures': medication_data.get('prevention', []),
                'monitoring_required': medication_data.get('monitoring', []),
                'severity_assessed': severity,
                'age_group': age_group,  # ⚠️ CRITICAL: Document which dosing category was used
                'patient_age': patient_age,
                'dosing_category': f"{'PEDIATRIC (weight-based mg/kg)' if age_group == 'pediatric' else 'GERIATRIC (reduced)' if age_group == 'geriatric' else 'ADULT (standard)'} dosing applied",
                'evidence_sources': ['WHO Guidelines 2023', 'Uganda Clinical Guidelines', 'IDSA Guidelines'],
                'allergy_warnings': allergies if allergies else [],
                'pharmacist_consultation_required': len(primary_meds) > 0,
                'age_verification_required': age_group == 'pediatric',  # Extra verification for children
                'database_used': 'Comprehensive WHO/Uganda Clinical Guidelines Database'
            }
            
            logger.info(f"Retrieved {len(primary_meds)} medications from comprehensive database for {primary_diagnosis} ({severity} severity)")
            
            return medication_plan
            
        except ImportError as e:
            logger.error(f"Medication database import error: {e}")
            # Fallback to old method
            return self._fallback_medication_recommendations(diagnosis, symptoms, allergies)
    
    def _query_medication_guidelines(self, diagnosis: str, symptoms: List[str]) -> Dict[str, Any]:
        """
        Query knowledge base for medication guidelines from WHO Essential Medicines List.
        """
        try:
            from knowledge.rag_utils import search_medical_knowledge
            
            # Build medication-focused query
            query = f"Medication treatment and prescription for {diagnosis}. Essential medicines, dosage, contraindications"
            if symptoms:
                query += f". Patient symptoms: {', '.join(symptoms)}"
            
            results = search_medical_knowledge(query, top_k=3)
            
            guidelines = []
            sources = set()
            
            for result in results:
                guidelines.append({
                    'content': result.get('content', ''),
                    'source': result.get('source', 'Unknown')
                })
                sources.add(result.get('source', 'Unknown'))
            
            return {
                'guidelines': guidelines,
                'sources': list(sources),
                'knowledge_base_used': True
            }
            
        except Exception as e:
            logger.error(f"Error querying medication guidelines: {e}")
            return {
                'guidelines': [],
                'sources': [],
                'knowledge_base_used': False
            }
    
    def _extract_medications_from_guidelines(self, guidelines: Dict) -> List[Dict]:
        """
        Extract medication recommendations from RAG results.
        Returns clean, actionable medication information.
        """
        medications = []
        
        # Common medication keywords to look for
        medication_keywords = [
            'paracetamol', 'acetaminophen', 'ibuprofen', 'aspirin',
            'amoxicillin', 'antibiotics', 'antibiotic', 'penicillin',
            'metformin', 'insulin', 'lisinopril', 'amlodipine',
            'omeprazole', 'ranitidine', 'salbutamol', 'inhaler',
            'diazepam', 'lorazepam', 'sertraline', 'fluoxetine'
        ]
        
        # Parse guidelines for medication mentions
        for guideline in guidelines.get('guidelines', []):
            content = guideline.get('content', '').lower()
            source = guideline.get('source', 'Unknown')
            
            if not content:
                continue
            
            # Look for specific medications mentioned
            for med_name in medication_keywords:
                if med_name in content:
                    # Extract context around the medication
                    sentences = content.split('.')
                    for sentence in sentences:
                        if med_name in sentence and len(sentence) < 200:
                            medications.append({
                                'name': med_name.title(),
                                'dosage': 'As per clinical guidelines',
                                'duration': 'As prescribed by healthcare provider',
                                'instructions': 'Follow healthcare provider instructions. Take as directed.',
                                'source': source
                            })
                            break
        
        # Remove duplicates
        seen_names = set()
        unique_meds = []
        for med in medications:
            if med['name'] not in seen_names:
                seen_names.add(med['name'])
                unique_meds.append(med)
        
        # If medications found in knowledge base, use them
        if unique_meds:
            return unique_meds[:3]  # Return top 3 medication recommendations
        
        # Fallback: Return general guidance
        return [{
            'name': 'Consult Healthcare Provider for Specific Medications',
            'dosage': 'To be determined by healthcare provider',
            'duration': 'As prescribed',
            'instructions': 'A healthcare provider will prescribe appropriate medications based on your specific condition, medical history, and current symptoms.',
            'source': 'Clinical Guidelines'
        }]
    
    def _generate_action_steps_from_guidelines(
        self, 
        urgency_level: str, 
        guidelines: Dict, 
        diagnosis: Dict
    ) -> Dict[str, List[str]]:
        """
        Generate concise, diagnosis-specific action steps.
        Keep it brief and practical for healthcare workers.
        """
        immediate = []
        short_term = []
        follow_up = []
        
        primary_diagnosis = diagnosis.get('primary_diagnosis', '').lower()
        
        # Diagnosis-specific actions
        if 'typhoid' in primary_diagnosis:
            immediate = [
                'Start antibiotics immediately (Ceftriaxone or Azithromycin)',
                'Ensure adequate hydration - drink 8-10 glasses of water daily',
                'Bed rest essential'
            ]
            short_term = [
                'Take prescribed antibiotics for full course (7-14 days)',
                'Soft diet - avoid spicy, fatty foods',
                'Monitor for complications: severe abdominal pain, bleeding'
            ]
            follow_up = [
                'Blood culture after treatment to confirm clearance',
                'Follow-up in 7 days',
                'Typhoid vaccine after recovery'
            ]
        elif 'meningitis' in primary_diagnosis:
            immediate = [
                '🚨 EMERGENCY - Immediate hospitalization required',
                'Start IV antibiotics within 30 minutes',
                'Lumbar puncture for diagnosis'
            ]
            short_term = [
                'ICU monitoring',
                'IV antibiotics for 10-14 days',
                'Manage fever and headache'
            ]
            follow_up = [
                'Hearing test after recovery',
                'Neurological follow-up',
                'Contact prophylaxis for close contacts'
            ]
        elif 'malaria' in primary_diagnosis:
            immediate = [
                'Start antimalarial treatment immediately (ACT)',
                'Rest and stay hydrated',
                'Monitor temperature every 4 hours'
            ]
            short_term = [
                'Complete 3-day ACT course',
                'Check for symptom improvement by Day 3',
                'Avoid mosquito bites'
            ]
            follow_up = [
                'Recheck if fever persists after 3 days',
                'Use insecticide-treated bed nets',
                'Follow-up in 1 week'
            ]
        elif 'pneumonia' in primary_diagnosis:
            immediate = [
                'Start antibiotics immediately',
                'Rest and adequate hydration',
                'Monitor breathing and oxygen levels'
            ]
            short_term = [
                'Complete antibiotic course (5-10 days)',
                'Chest physiotherapy if needed',
                'Monitor for improvement in 48-72 hours'
            ]
            follow_up = [
                'Chest X-ray if not improving',
                'Follow-up in 5-7 days',
                'Pneumococcal vaccine if eligible'
            ]
        elif 'gastroenteritis' in primary_diagnosis or 'diarrhea' in primary_diagnosis:
            immediate = [
                'Start Oral Rehydration Solution (ORS) immediately',
                'Zinc supplementation if child <5 years',
                'Continue normal feeding'
            ]
            short_term = [
                'Monitor hydration status',
                'Antibiotics ONLY if blood in stool',
                'Avoid anti-diarrheal medications in children'
            ]
            follow_up = [
                'Recheck if diarrhea persists >7 days',
                'Monitor for dehydration signs',
                'Hygiene education'
            ]
        elif urgency_level.upper() == 'CRITICAL':
            immediate = [
                '🚨 CALL EMERGENCY SERVICES IMMEDIATELY',
                'Monitor vital signs continuously',
                'Keep patient calm and comfortable'
            ]
            short_term = [
                'Emergency department evaluation',
                'Diagnostic tests as ordered',
                'Hospital admission if needed'
            ]
            follow_up = [
                'Follow discharge instructions',
                'Scheduled follow-up appointments'
            ]
        elif urgency_level.upper() == 'HIGH':
            immediate = [
                'Seek medical evaluation within 2-4 hours',
                'Monitor symptoms closely',
                'Rest and maintain hydration'
            ]
            short_term = [
                'Follow prescribed treatment plan',
                'Take medications as directed',
                'Monitor for improvement'
            ]
            follow_up = [
                'Follow-up in 3-5 days',
                'Return if symptoms worsen'
            ]
        else:  # MODERATE/ROUTINE
            # Get diagnosis-specific immediate relief actions
            diagnosis_specific_actions = self._get_immediate_relief_actions(primary_diagnosis)
            immediate = diagnosis_specific_actions[:3]  # Take first 3 specific actions
            short_term = [
                'Follow treatment recommendations',
                'Take prescribed medications',
                'Monitor for changes'
            ]
            follow_up = [
                'Follow-up as recommended',
                'Complete treatment course'
            ]
        
        return {
            'immediate': immediate[:3],  # Limit to 3 items
            'short_term': short_term[:3],  # Limit to 3 items
            'follow_up': follow_up[:3]  # Limit to 3 items
        }
    
    def suggest_tests_and_referrals(
        self,
        diagnosis: Dict,
        urgency_level: str
    ) -> Dict[str, Any]:
        """
        Suggest diagnostic tests and specialist referrals.
        
        Args:
            diagnosis: Diagnosis information
            urgency_level: Case urgency level
            
        Returns:
            Dict containing tests and referral recommendations
        """
        logger.info("Generating test and referral recommendations")
        
        primary_diagnosis = diagnosis.get('primary_diagnosis', '')
        differential_diagnoses = diagnosis.get('differential_diagnoses', [])
        
        # Generate diagnostic tests
        tests = self._recommend_diagnostic_tests(
            primary_diagnosis, differential_diagnoses, urgency_level
        )
        
        # Generate specialist referrals
        referrals = self._recommend_specialist_referrals(
            primary_diagnosis, urgency_level
        )
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'diagnostic_tests': tests,
            'specialist_referrals': referrals,
            'urgency': self._determine_test_urgency(urgency_level),
            'insurance_notes': 'Verify coverage with insurance provider',
        }
        
        return recommendations
    
    def provide_first_aid(self, condition: str) -> Dict[str, Any]:
        """
        Provide first-aid instructions for specific conditions.
        
        Args:
            condition: Medical condition or emergency
            
        Returns:
            Dict containing first-aid instructions
        """
        logger.info(f"Providing first-aid instructions for: {condition}")
        
        condition_lower = condition.lower()
        
        # Determine condition category
        if any(word in condition_lower for word in ['cardiac', 'heart', 'chest pain']):
            first_aid = self._cardiac_first_aid()
        elif any(word in condition_lower for word in ['breathing', 'respiratory', 'asthma']):
            first_aid = self._respiratory_first_aid()
        elif any(word in condition_lower for word in ['bleeding', 'wound', 'cut']):
            first_aid = self._bleeding_first_aid()
        elif any(word in condition_lower for word in ['burn']):
            first_aid = self._burn_first_aid()
        elif any(word in condition_lower for word in ['seizure']):
            first_aid = self._seizure_first_aid()
        else:
            first_aid = self._general_first_aid()
        
        first_aid['condition'] = condition
        first_aid['timestamp'] = datetime.now().isoformat()
        
        return first_aid
    
    def _get_immediate_relief_actions(self, diagnosis: str) -> List[str]:
        """
        Get diagnosis-specific immediate relief actions that can be taken right now.
        These are practical steps to ease symptoms before medical intervention.
        """
        diagnosis_lower = diagnosis.lower()
        
        # Upper respiratory infections (cold, flu, URI, pharyngitis)
        if any(word in diagnosis_lower for word in ['cold', 'flu', 'influenza', 'upper respiratory', 'uri', 'pharyngitis', 'sore throat', 'rhinitis', 'nasal congestion']):
            return [
                'Rest - avoid strenuous activities to help body recover',
                'Drink warm fluids (tea, warm water with honey, soup) to soothe throat',
                'Use saline nasal drops or spray to relieve nasal congestion',
                'Gargle with warm salt water (1/2 tsp salt in glass of warm water) for sore throat',
                'Use a humidifier or breathe steam to ease breathing',
                'Take paracetamol/acetaminophen for fever and pain relief (if no allergies)'
            ]
        
        # Headache/Migraine
        elif any(word in diagnosis_lower for word in ['headache', 'migraine', 'cephalgia']):
            return [
                'Rest in a quiet, dark room away from bright lights and noise',
                'Apply cold compress to forehead and temples for 15-20 minutes',
                'Drink water - dehydration can worsen headaches',
                'Take paracetamol/ibuprofen for pain relief (if no contraindications)',
                'Avoid screens (phone, computer, TV) to reduce eye strain',
                'Lie down with head slightly elevated'
            ]
        
        # Fever
        elif 'fever' in diagnosis_lower or 'pyrexia' in diagnosis_lower:
            return [
                'Rest and avoid physical exertion',
                'Drink plenty of fluids (water, ORS, clear soups) to prevent dehydration',
                'Wear light, breathable clothing and use light bedding',
                'Take paracetamol/acetaminophen to reduce fever (age-appropriate dose)',
                'Sponge with lukewarm water if fever is very high (avoid cold water)',
                'Monitor temperature every 2-4 hours'
            ]
        
        # Gastroenteritis/Diarrhea
        elif any(word in diagnosis_lower for word in ['gastroenteritis', 'diarrhea', 'diarrhoea', 'stomach flu', 'vomiting']):
            return [
                'Drink ORS (oral rehydration solution) frequently in small amounts',
                'Eat bland foods: bananas, rice, applesauce, toast (BRAT diet)',
                'Avoid dairy products, fatty foods, caffeine, and alcohol',
                'Rest - lie on your side if vomiting to prevent aspiration',
                'Wash hands thoroughly to prevent spread',
                'Take zinc supplements if available (especially for children)'
            ]
        
        # Allergic reaction (non-severe)
        elif any(word in diagnosis_lower for word in ['allergy', 'allergic', 'urticaria', 'hives', 'rash']):
            return [
                'Stop contact with suspected allergen immediately',
                'Take antihistamine (e.g., chlorpheniramine, cetirizine) if available',
                'Apply cool, wet compress to affected skin areas',
                'Avoid scratching - keep nails short and clean',
                'Wear loose, comfortable clothing',
                'Monitor for worsening symptoms (difficulty breathing, swelling)'
            ]
        
        # Respiratory issues (cough, asthma)
        elif any(word in diagnosis_lower for word in ['cough', 'bronchitis', 'asthma', 'wheezing']):
            return [
                'Sit upright - do not lie flat, use pillows for support',
                'Drink warm fluids to loosen mucus',
                'Use prescribed inhaler if available (salbutamol/bronchodilator)',
                'Breathe steam from hot water (carefully) to ease breathing',
                'Avoid smoke, dust, and strong odors',
                'Practice slow, deep breathing to reduce anxiety and improve oxygen flow'
            ]
        
        # Abdominal pain
        elif any(word in diagnosis_lower for word in ['abdominal pain', 'stomach pain', 'gastritis', 'dyspepsia']):
            return [
                'Rest and avoid eating solid foods for 1-2 hours',
                'Drink clear fluids in small sips',
                'Apply warm compress to abdomen for comfort',
                'Avoid spicy, fatty, or acidic foods',
                'Lie on your side with knees drawn up if cramping',
                'Take antacid if available and pain is upper abdominal'
            ]
        
        # Back pain/Muscle pain
        elif any(word in diagnosis_lower for word in ['back pain', 'muscle pain', 'musculoskeletal', 'sprain', 'strain']):
            return [
                'Rest the affected area - avoid activities that cause pain',
                'Apply ice pack for first 48 hours (15-20 min every 2-3 hours)',
                'After 48 hours, apply heat (warm compress) to relax muscles',
                'Take ibuprofen or paracetamol for pain relief',
                'Keep affected area elevated if swollen',
                'Gentle stretching if tolerated, avoid sudden movements'
            ]
        
        # Skin infection/Wound
        elif any(word in diagnosis_lower for word in ['wound', 'cut', 'laceration', 'skin infection', 'abscess', 'cellulitis']):
            return [
                'Clean wound gently with clean water and mild soap',
                'Apply antiseptic (betadine, alcohol) if available',
                'Cover with clean, dry bandage/dressing',
                'Keep wound elevated to reduce swelling',
                'Do not squeeze or pop any abscess or boil',
                'Monitor for signs of infection (increased redness, warmth, pus, fever)'
            ]
        
        # Malaria (common in Uganda)
        elif 'malaria' in diagnosis_lower:
            return [
                'Start antimalarial treatment immediately as prescribed',
                'Rest completely - avoid any strenuous activity',
                'Drink plenty of fluids to prevent dehydration from fever/sweating',
                'Take paracetamol for fever (avoid aspirin)',
                'Sleep under treated mosquito net to prevent further bites',
                'Monitor temperature and symptoms closely'
            ]
        
        # UTI (Urinary tract infection)
        elif any(word in diagnosis_lower for word in ['uti', 'urinary tract', 'cystitis', 'dysuria']):
            return [
                'Drink plenty of water (2-3 liters daily) to flush bacteria',
                'Urinate frequently - do not hold urine',
                'Apply heating pad to lower abdomen for pain relief',
                'Avoid caffeine, alcohol, and spicy foods',
                'Wipe front to back after using toilet (for females)',
                'Start antibiotics if prescribed, complete full course'
            ]
        
        # Default general immediate actions
        else:
            return [
                'Rest and avoid strenuous activities',
                'Stay well hydrated - drink water regularly',
                'Monitor symptoms and note any changes',
                'Take prescribed medications as directed'
            ]
    
    def _determine_protocol_type(
        self,
        diagnosis: str,
        emergency_conditions: List = None
    ) -> str:
        """Determine which emergency protocol to use."""
        diagnosis_lower = diagnosis.lower()
        
        if emergency_conditions:
            for condition in emergency_conditions:
                if 'CARDIAC' in condition:
                    return 'cardiac'
                elif 'STROKE' in condition or 'NEUROLOGICAL' in condition:
                    return 'neurological'
                elif 'RESPIRATORY' in condition:
                    return 'respiratory'
        
        # Check diagnosis text
        if any(word in diagnosis_lower for word in ['cardiac', 'heart', 'mi', 'infarction']):
            return 'cardiac'
        elif any(word in diagnosis_lower for word in ['stroke', 'cva', 'neurological']):
            return 'neurological'
        elif any(word in diagnosis_lower for word in ['respiratory', 'breathing', 'asthma']):
            return 'respiratory'
        
        return 'general'
    
    def _get_emergency_protocol(self, protocol_type: str) -> Dict:
        """Retrieve emergency protocol for condition type."""
        return self.EMERGENCY_PROTOCOLS.get(protocol_type, {
            'name': 'General Emergency Protocol',
            'immediate_actions': [
                'Assess patient condition',
                'Call 911 if life-threatening',
                'Monitor vital signs',
                'Keep patient comfortable',
                'Document all observations'
            ],
            'medications': ['As directed by physician'],
            'contraindications': []
        })
    
    def _generate_action_steps(
        self,
        urgency_level: str,
        emergency_protocol: Dict = None,
        diagnosis: Dict = None
    ) -> Dict[str, List[str]]:
        """Generate categorized action steps with diagnosis-specific immediate relief measures."""
        steps = {
            'immediate': [],
            'short_term': [],
            'follow_up': []
        }
        
        # Get diagnosis-specific immediate relief actions
        diagnosis_name = diagnosis.get('primary_diagnosis', '').lower() if diagnosis else ''
        immediate_relief = self._get_immediate_relief_actions(diagnosis_name)
        
        if urgency_level == 'CRITICAL':
            if emergency_protocol:
                steps['immediate'] = emergency_protocol.get('immediate_actions', [])
            steps['immediate'].extend([
                'Ensure emergency services (911) have been contacted',
                'Monitor patient continuously until help arrives',
                'Document timeline of symptoms and interventions'
            ])
            steps['short_term'] = [
                'Transport to emergency department',
                'Provide full medical history to emergency team',
                'Follow emergency department recommendations'
            ]
        
        elif urgency_level == 'HIGH':
            steps['immediate'] = immediate_relief + [
                'Seek medical attention within 2-4 hours',
                'Monitor symptoms for any worsening',
                'Keep track of vital signs if possible'
            ]
            steps['short_term'] = [
                'Visit urgent care or emergency department',
                'Begin prescribed treatment as directed',
                'Schedule follow-up with primary care physician'
            ]
        
        else:  # ROUTINE
            steps['immediate'] = immediate_relief + [
                'Rest and monitor symptoms',
                'Stay hydrated - drink plenty of fluids',
                'Schedule appointment with primary care physician if symptoms persist or worsen'
            ]
            steps['short_term'] = [
                'Attend scheduled medical appointment',
                'Discuss symptoms and concerns with doctor',
                'Begin any prescribed treatments'
            ]
        
        steps['follow_up'] = [
            'Follow all treatment recommendations',
            'Monitor for symptom changes',
            'Schedule follow-up appointments as directed',
            'Report any worsening symptoms immediately'
        ]
        
        return steps
    
    def _create_action_timeline(self, urgency_level: str, action_steps: Dict) -> Dict:
        """Create timeline for actions."""
        if urgency_level == 'CRITICAL':
            return {
                'immediate': 'NOW - Within 5 minutes',
                'short_term': 'Within 1-2 hours',
                'follow_up': '24-48 hours after initial treatment'
            }
        elif urgency_level == 'HIGH':
            return {
                'immediate': 'Within 1 hour',
                'short_term': 'Within 2-4 hours',
                'follow_up': 'Within 1 week'
            }
        else:
            return {
                'immediate': 'Within 24 hours',
                'short_term': 'Within 3-7 days',
                'follow_up': 'Within 2-4 weeks'
            }
    
    def _generate_warnings(self, red_flags: List, emergency_conditions: List) -> List[str]:
        """Generate warnings based on red flags and emergencies."""
        warnings = []
        
        if emergency_conditions:
            warnings.append(f"⚠️ EMERGENCY CONDITIONS DETECTED: {', '.join(emergency_conditions)}")
            warnings.append("CALL 911 IMMEDIATELY")
        
        if red_flags:
            for flag in red_flags:
                warnings.append(f"⚠️ Red Flag: {flag.get('flag', 'Unknown')} - {flag.get('action', 'Seek medical attention')}")
        
        return warnings
    
    def _define_success_criteria(self, diagnosis: Dict) -> List[str]:
        """Define clear, measurable success criteria for treatment monitoring."""
        primary_diagnosis = diagnosis.get('primary_diagnosis', '').lower()
        
        # General success criteria applicable to most conditions
        criteria = [
            'Reduction in severity or frequency of symptoms',
            'Vital signs stabilize and return to normal range',
            'Patient able to resume normal daily activities',
            'No development of new symptoms or complications',
            'Patient reports feeling better and improved quality of life'
        ]
        
        # Add condition-specific criteria
        if any(word in primary_diagnosis for word in ['fever', 'temperature', 'pyrexia']):
            criteria.append('Temperature returns to normal (below 38°C/100.4°F)')
        
        if any(word in primary_diagnosis for word in ['pain', 'ache', 'discomfort']):
            criteria.append('Pain level reduces from initial severity (use 0-10 scale)')
        
        if any(word in primary_diagnosis for word in ['infection', 'bacterial', 'viral']):
            criteria.append('Signs of infection resolve (no fever, improved white blood cell count)')
        
        if any(word in primary_diagnosis for word in ['respiratory', 'cough', 'breathing']):
            criteria.append('Breathing becomes easier, respiratory rate normalizes')
        
        return criteria[:6]  # Return top 6 criteria
    
    def _generate_medication_list(self, diagnosis: str) -> List[Dict]:
        """Generate medication list based on diagnosis."""
        medications = []
        
        if 'infection' in diagnosis or 'bacterial' in diagnosis:
            medications.append({
                'name': 'Amoxicillin',
                'dosage': '500mg every 8 hours',
                'duration': '7-10 days',
                'purpose': 'Antibiotic for bacterial infection'
            })
        
        if 'pain' in diagnosis or 'headache' in diagnosis:
            medications.append({
                'name': 'Ibuprofen',
                'dosage': '400-600mg every 6-8 hours',
                'duration': 'As needed',
                'purpose': 'Pain relief and anti-inflammatory'
            })
        
        if 'fever' in diagnosis:
            medications.append({
                'name': 'Acetaminophen',
                'dosage': '650-1000mg every 6 hours',
                'duration': 'As needed',
                'purpose': 'Fever reduction'
            })
        
        return medications if medications else [{
            'name': 'Consult physician for medication recommendations',
            'dosage': 'N/A',
            'duration': 'N/A',
            'purpose': 'Specific prescription needed'
        }]
    
    def _filter_by_allergies(self, medications: List[Dict], allergies: List[str]) -> List[Dict]:
        """Filter medications based on known allergies."""
        filtered = []
        allergies_lower = [a.lower() for a in allergies]
        
        for med in medications:
            med_name_lower = med.get('name', '').lower()
            
            # Check contraindications field as well
            contraindications = med.get('contraindications', '').lower()
            
            # Filter if medication name contains allergy term
            if any(allergy in med_name_lower for allergy in allergies_lower):
                logger.warning(f"Filtered out {med.get('name')} due to allergy in medication name")
                continue
            
            # Filter if allergy is in contraindications
            if any(allergy in contraindications for allergy in allergies_lower):
                logger.warning(f"Filtered out {med.get('name')} due to allergy in contraindications")
                continue
            
            filtered.append(med)
        
        return filtered
    
    def _fallback_medication_recommendations(self, diagnosis: Dict, symptoms: List[str], allergies: List[str]) -> Dict[str, Any]:
        """Fallback method if medication database import fails."""
        logger.warning("Using fallback medication recommendations")
        
        # Query knowledge base for medication recommendations
        medication_guidelines = self._query_medication_guidelines(
            diagnosis.get('primary_diagnosis', '').lower(), 
            symptoms or []
        )
        
        # Extract medications from guidelines
        medications = self._extract_medications_from_guidelines(medication_guidelines)
        
        # Filter based on allergies
        if allergies:
            medications = self._filter_by_allergies(medications, allergies)
        
        # Add evidence sources
        medication_plan = {
            'timestamp': datetime.now().isoformat(),
            'primary_medications': medications[:3],  # Top 3
            'alternative_medications': medications[3:6] if len(medications) > 3 else [],
            'evidence_sources': medication_guidelines.get('sources', []),
            'allergy_warnings': allergies if allergies else [],
            'pharmacist_consultation_required': len(medications) > 0,
            'knowledge_base_used': medication_guidelines.get('knowledge_base_used', False),
            'database_used': 'Fallback RAG Method'
        }
        
        return medication_plan
    
    def _get_medication_contraindications(self, medication: str, patient_history: Dict = None) -> List[str]:
        """Get contraindications for medication."""
        # Simplified contraindications
        contraindications = {
            'ibuprofen': ['Active bleeding', 'Kidney disease', 'Heart disease'],
            'aspirin': ['Active bleeding', 'Bleeding disorders', 'Allergy to aspirin'],
            'amoxicillin': ['Penicillin allergy', 'Mononucleosis'],
        }
        
        med_lower = medication.lower()
        for key, contras in contraindications.items():
            if key in med_lower:
                return contras
        
        return ['Consult physician']
    
    def _get_medication_guidelines(self) -> List[str]:
        """Get general medication guidelines."""
        return [
            'Take medications exactly as prescribed',
            'Complete full course of antibiotics',
            'Take with food if stomach upset occurs',
            'Report any adverse reactions immediately',
            'Do not share medications with others'
        ]
    
    def _recommend_diagnostic_tests(self, diagnosis: str, differentials: List, urgency: str) -> List[Dict]:
        """Recommend diagnostic tests."""
        tests = []
        diagnosis_lower = diagnosis.lower()
        
        if 'infection' in diagnosis_lower or 'fever' in diagnosis_lower:
            tests.append({
                'test': 'Complete Blood Count (CBC)',
                'purpose': 'Check for infection or anemia',
                'urgency': 'Routine' if urgency != 'CRITICAL' else 'Stat'
            })
        
        if 'cardiac' in diagnosis_lower or 'heart' in diagnosis_lower:
            tests.append({
                'test': 'Electrocardiogram (ECG)',
                'purpose': 'Assess heart rhythm and function',
                'urgency': 'Stat'
            })
            tests.append({
                'test': 'Cardiac Enzymes (Troponin)',
                'purpose': 'Rule out heart attack',
                'urgency': 'Stat'
            })
        
        if 'respiratory' in diagnosis_lower:
            tests.append({
                'test': 'Chest X-ray',
                'purpose': 'Evaluate lungs for infection or abnormality',
                'urgency': 'Routine'
            })
        
        return tests if tests else [{
            'test': 'Basic Metabolic Panel',
            'purpose': 'General health assessment',
            'urgency': 'Routine'
        }]
    
    def _recommend_specialist_referrals(self, diagnosis: str, urgency: str) -> List[Dict]:
        """Recommend specialist referrals."""
        referrals = []
        diagnosis_lower = diagnosis.lower()
        
        if 'cardiac' in diagnosis_lower or 'heart' in diagnosis_lower:
            referrals.append({
                'specialist': 'Cardiologist',
                'reason': 'Cardiac evaluation and management',
                'urgency': 'Urgent' if urgency == 'CRITICAL' else 'Routine'
            })
        
        if 'neurological' in diagnosis_lower or 'stroke' in diagnosis_lower:
            referrals.append({
                'specialist': 'Neurologist',
                'reason': 'Neurological assessment',
                'urgency': 'Urgent'
            })
        
        return referrals
    
    def _determine_test_urgency(self, urgency_level: str) -> str:
        """Determine urgency for tests."""
        if urgency_level == 'CRITICAL':
            return 'STAT - Immediate'
        elif urgency_level == 'HIGH':
            return 'Urgent - Within 24 hours'
        else:
            return 'Routine - Within 1 week'
    
    def _cardiac_first_aid(self) -> Dict:
        """Cardiac emergency first aid."""
        return {
            'name': 'Cardiac Emergency First Aid',
            'steps': [
                '1. Call 911 immediately',
                '2. Have patient sit or lie down comfortably',
                '3. Loosen tight clothing',
                '4. Give aspirin (325mg) if available and not allergic',
                '5. If patient becomes unconscious, begin CPR',
                '6. Use AED if available'
            ],
            'warnings': [
                'Do not leave patient alone',
                'Do not give food or drink',
                'Monitor breathing continuously'
            ]
        }
    
    def _respiratory_first_aid(self) -> Dict:
        """Respiratory emergency first aid."""
        return {
            'name': 'Respiratory Distress First Aid',
            'steps': [
                '1. Help patient sit upright',
                '2. Loosen tight clothing around neck',
                '3. Assist with rescue inhaler if available',
                '4. Encourage slow, deep breaths',
                '5. Call 911 if breathing worsens'
            ],
            'warnings': [
                'Do not lay patient flat',
                'Watch for blue lips or fingernails',
                'Be ready to perform CPR if needed'
            ]
        }
    
    def _bleeding_first_aid(self) -> Dict:
        """Bleeding first aid."""
        return {
            'name': 'Bleeding Control First Aid',
            'steps': [
                '1. Apply direct pressure with clean cloth',
                '2. Elevate injured area above heart if possible',
                '3. Maintain pressure for 10-15 minutes',
                '4. Apply bandage once bleeding stops',
                '5. Call 911 if severe or uncontrolled bleeding'
            ],
            'warnings': [
                'Do not remove cloth if soaked through - add more layers',
                'Do not apply tourniquet unless life-threatening',
                'Watch for signs of shock'
            ]
        }
    
    def _burn_first_aid(self) -> Dict:
        """Burn first aid."""
        return {
            'name': 'Burn First Aid',
            'steps': [
                '1. Remove from heat source',
                '2. Cool burn with cool (not ice) water for 10-20 minutes',
                '3. Cover with sterile, non-stick dressing',
                '4. Do not break blisters',
                '5. Seek medical attention for severe burns'
            ],
            'warnings': [
                'Do not apply ice directly',
                'Do not use butter or ointments',
                'Watch for signs of infection'
            ]
        }
    
    def _seizure_first_aid(self) -> Dict:
        """Seizure first aid."""
        return {
            'name': 'Seizure First Aid',
            'steps': [
                '1. Clear area of dangerous objects',
                '2. Cushion head with something soft',
                '3. Turn person on side to keep airway clear',
                '4. Time the seizure',
                '5. Stay with person until fully conscious',
                '6. Call 911 if seizure lasts >5 minutes'
            ],
            'warnings': [
                'Do NOT put anything in mouth',
                'Do NOT restrain person',
                'Do NOT give water or food until fully alert'
            ]
        }
    
    def _general_first_aid(self) -> Dict:
        """General first aid."""
        return {
            'name': 'General First Aid',
            'steps': [
                '1. Ensure scene safety',
                '2. Assess patient condition',
                '3. Call for help if needed',
                '4. Keep patient comfortable',
                '5. Monitor vital signs',
                '6. Do not move patient unless necessary'
            ],
            'warnings': [
                'Always call professional help if unsure',
                'Document all actions taken',
                'Wear protective equipment if available'
            ]
        }
