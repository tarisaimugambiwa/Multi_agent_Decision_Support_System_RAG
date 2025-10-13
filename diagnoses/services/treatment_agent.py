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
        allergies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate evidence-based medication recommendations from WHO Essential Medicines List.
        
        Args:
            diagnosis: Diagnosis information
            symptoms: List of symptoms
            patient_history: Patient medical history
            allergies: List of known allergies
            
        Returns:
            Dict containing medication recommendations with evidence
        """
        logger.info(f"Generating evidence-based medication recommendations for: {diagnosis.get('primary_diagnosis', 'unknown')}")
        
        primary_diagnosis = diagnosis.get('primary_diagnosis', '').lower()
        
        # Query knowledge base for medication recommendations
        medication_guidelines = self._query_medication_guidelines(primary_diagnosis, symptoms or [])
        
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
            'knowledge_base_used': medication_guidelines.get('knowledge_base_used', False)
        }
        
        return medication_plan
    
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
        Returns actual medication information from knowledge base.
        """
        medications = []
        
        # Parse guidelines for medication mentions
        for guideline in guidelines.get('guidelines', []):
            content = guideline.get('content', '')
            source = guideline.get('source', 'Unknown')
            
            if not content:
                continue
            
            # Extract sentences that mention medications
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                # Look for medication-related keywords
                if any(keyword in sentence_lower for keyword in [
                    'medication', 'drug', 'medicine', 'administer', 'prescribe',
                    'tablet', 'capsule', 'injection', 'dose', 'mg', 'ml',
                    'treatment includes', 'give', 'oral', 'intravenous'
                ]):
                    # Extract the full sentence as medication guidance
                    medications.append({
                        'name': sentence,  # Store the full guidance
                        'dosage': 'As specified in medical guidelines',
                        'duration': 'Per treatment protocol',
                        'instructions': f'Source: {source}',
                        'source': source
                    })
        
        # If medications found in knowledge base, use them
        if medications:
            return medications[:5]  # Return top 5 medication recommendations
        
        # Fallback: Return condition-specific guidance
        return [{
            'name': 'Medication recommendations available in knowledge base',
            'dosage': 'Per clinical guidelines',
            'duration': 'As prescribed by healthcare provider',
            'instructions': 'Consult full medical guidelines for specific medication protocols, dosages, and contraindications based on patient condition and history.',
            'source': 'WHO Essential Medicines List and Treatment Guidelines'
        }]
    
    def _generate_action_steps_from_guidelines(
        self, 
        urgency_level: str, 
        guidelines: Dict, 
        diagnosis: Dict
    ) -> Dict[str, List[str]]:
        """
        Generate action steps based on retrieved treatment guidelines.
        """
        immediate = []
        short_term = []
        follow_up = []
        
        # Extract detailed recommendations from guidelines
        if guidelines.get('guidelines'):
            for guideline in guidelines['guidelines']:  # Use all available guidelines
                content = guideline.get('content', '').strip()
                source = guideline.get('source', 'medical literature')
                
                if not content:
                    continue
                
                # Extract actionable information from the guideline content
                # Split content into sentences for better parsing
                sentences = [s.strip() for s in content.split('.') if s.strip()]
                
                for sentence in sentences[:5]:  # Use first 5 sentences of each guideline
                    sentence_lower = sentence.lower()
                    
                    # Categorize based on keywords and urgency
                    if any(word in sentence_lower for word in ['immediate', 'urgent', 'emergency', 'critical', 'now', 'immediately']):
                        if urgency_level in ['CRITICAL', 'HIGH'] and sentence not in immediate:
                            immediate.append(f"{sentence}")
                    
                    elif any(word in sentence_lower for word in ['administer', 'give', 'provide', 'treat', 'medication', 'drug', 'therapy']):
                        if sentence not in short_term:
                            short_term.append(f"{sentence}")
                    
                    elif any(word in sentence_lower for word in ['monitor', 'observe', 'follow-up', 'reassess', 'review', 'track']):
                        if sentence not in follow_up:
                            follow_up.append(f"{sentence}")
                    
                    # If sentence has treatment info but doesn't match above, add to short-term
                    elif any(word in sentence_lower for word in ['treatment', 'manage', 'care', 'intervention']) and sentence not in short_term:
                        short_term.append(f"{sentence}")
        
        # Add standard emergency steps based on urgency
        if urgency_level == 'CRITICAL':
            immediate.insert(0, '🚨 CALL EMERGENCY SERVICES IMMEDIATELY OR GO TO NEAREST EMERGENCY DEPARTMENT')
            immediate.insert(1, 'Monitor vital signs continuously (blood pressure, heart rate, breathing)')
            immediate.insert(2, 'Keep patient calm and in a comfortable position')
            if not any('oxygen' in action.lower() for action in immediate):
                immediate.append('Prepare to administer oxygen if available')
        elif urgency_level == 'HIGH':
            immediate.insert(0, '⚠️ Seek urgent medical evaluation within 2-4 hours')
            immediate.append('Monitor symptoms closely and document any changes')
            immediate.append('Have patient rest and avoid strenuous activity')
        else:
            immediate.append('Schedule medical consultation within 24-48 hours')
            immediate.append('Monitor symptoms and document progression')
        
        # Add standard short-term actions if none from guidelines
        if not short_term:
            short_term.append('Follow treatment plan as prescribed by healthcare provider')
            short_term.append('Take all medications as directed (complete full course)')
            short_term.append('Maintain adequate hydration and nutrition')
            short_term.append('Get adequate rest to support recovery')
        
        # Add standard follow-up if none from guidelines
        if not follow_up:
            follow_up.append('Schedule follow-up appointment in 3-7 days or as directed')
            follow_up.append('Report immediately if symptoms worsen or new symptoms develop')
            follow_up.append('Keep a symptom diary to track progress')
            follow_up.append('Return to emergency department if condition deteriorates')
        
        return {
            'immediate': immediate[:10],  # Limit to 10 items for readability
            'short_term': short_term[:10],
            'follow_up': follow_up[:8]
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
        """Generate categorized action steps."""
        steps = {
            'immediate': [],
            'short_term': [],
            'follow_up': []
        }
        
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
            steps['immediate'] = [
                'Seek medical attention within 2-4 hours',
                'Monitor symptoms for any worsening',
                'Have patient rest in comfortable position',
                'Keep track of vital signs if possible'
            ]
            steps['short_term'] = [
                'Visit urgent care or emergency department',
                'Begin prescribed treatment as directed',
                'Schedule follow-up with primary care physician'
            ]
        
        else:  # ROUTINE
            steps['immediate'] = [
                'Schedule appointment with primary care physician',
                'Rest and monitor symptoms',
                'Stay hydrated and maintain comfort'
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
        """Define success criteria for treatment."""
        return [
            'Symptom improvement within expected timeframe',
            'No worsening of condition',
            'Vital signs return to normal range',
            'Patient able to perform daily activities',
            'Follow-up appointments completed'
        ]
    
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
            med_name_lower = med['name'].lower()
            if not any(allergy in med_name_lower for allergy in allergies_lower):
                filtered.append(med)
            else:
                logger.warning(f"Filtered out {med['name']} due to allergy")
        
        return filtered
    
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
