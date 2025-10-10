"""
COORDINATOR AGENT - ⚙️ Workflow Management & Case Routing

RESPONSIBILITIES:
- Route patient cases based on symptom severity
- Assign priority levels (low, medium, high, urgent, critical)
- Manage workflow between different agents
- Escalate critical cases to human doctors
- Coordinate multi-agent decision making
"""

import logging
from typing import Dict, Any, Tuple
from django.utils import timezone

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Coordinator Agent manages the overall workflow and routes cases to appropriate specialists.
    Acts as the central orchestrator for the multi-agent system.
    """
    
    PRIORITY_LEVELS = {
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3,
        'URGENT': 4,
        'CRITICAL': 5,
    }
    
    CRITICAL_KEYWORDS = [
        'chest pain', 'heart attack', 'cardiac arrest', 'stroke',
        'severe bleeding', 'unconscious', 'not breathing', 'seizure',
        'anaphylaxis', 'severe allergic reaction', 'difficulty breathing',
        'severe head injury', 'overdose', 'poisoning'
    ]
    
    URGENT_KEYWORDS = [
        'severe pain', 'high fever', 'vomiting blood', 'confusion',
        'severe headache', 'blurred vision', 'rapid heartbeat',
        'shortness of breath', 'severe abdominal pain'
    ]
    
    def __init__(self):
        """Initialize the Coordinator Agent."""
        self.name = "Coordinator Agent"
        logger.info(f"{self.name} initialized")
    
    def route_case(self, case, symptoms: str, vital_signs: Dict = None) -> Dict[str, Any]:
        """
        Route a patient case based on symptoms and vital signs.
        
        Args:
            case: The Case model instance
            symptoms: Patient symptoms description
            vital_signs: Dictionary of vital signs
            
        Returns:
            Dict with routing decision, priority, and required agents
        """
        logger.info(f"Routing case #{case.id} for patient {case.patient.first_name} {case.patient.last_name}")
        
        # Analyze urgency
        urgency_score, urgency_level = self._assess_urgency(symptoms, vital_signs)
        
        # Determine priority
        priority = self._assign_priority(urgency_level, vital_signs)
        
        # Determine which agents to involve
        required_agents = self._determine_required_agents(urgency_level, symptoms)
        
        # Decide if doctor review is needed
        needs_doctor_review = self._should_escalate_to_doctor(urgency_level, urgency_score)
        
        # Create routing decision
        routing_decision = {
            'priority': priority,
            'urgency_level': urgency_level,
            'urgency_score': urgency_score,
            'required_agents': required_agents,
            'needs_doctor_review': needs_doctor_review,
            'recommended_status': 'DOCTOR_REVIEW' if needs_doctor_review else 'PENDING',
            'routing_reason': self._generate_routing_reason(urgency_level, urgency_score),
            'timestamp': timezone.now().isoformat(),
        }
        
        logger.info(f"Case #{case.id} routed: Priority={priority}, Urgency={urgency_level}, Doctor Review={needs_doctor_review}")
        
        return routing_decision
    
    def _assess_urgency(self, symptoms: str, vital_signs: Dict = None) -> Tuple[int, str]:
        """
        Assess the urgency level based on symptoms and vital signs.
        
        Returns:
            Tuple of (urgency_score, urgency_level)
        """
        symptoms_lower = symptoms.lower()
        urgency_score = 0
        
        # Check for critical keywords
        critical_count = sum(1 for keyword in self.CRITICAL_KEYWORDS if keyword in symptoms_lower)
        if critical_count > 0:
            urgency_score += critical_count * 30
        
        # Check for urgent keywords
        urgent_count = sum(1 for keyword in self.URGENT_KEYWORDS if keyword in symptoms_lower)
        if urgent_count > 0:
            urgency_score += urgent_count * 15
        
        # Analyze vital signs
        if vital_signs:
            vital_score = self._analyze_vital_signs(vital_signs)
            urgency_score += vital_score
        
        # Determine urgency level
        if urgency_score >= 80:
            urgency_level = 'critical'
        elif urgency_score >= 50:
            urgency_level = 'high'
        elif urgency_score >= 25:
            urgency_level = 'moderate'
        else:
            urgency_level = 'low'
        
        return urgency_score, urgency_level
    
    def _analyze_vital_signs(self, vital_signs: Dict) -> int:
        """
        Analyze vital signs and return urgency score contribution.
        
        Returns:
            Urgency score (0-40)
        """
        score = 0
        
        # Temperature analysis
        if 'temperature' in vital_signs:
            temp = float(vital_signs['temperature'])
            if temp >= 103 or temp <= 95:  # Very high or very low
                score += 20
            elif temp >= 101 or temp <= 96:  # High or low
                score += 10
        
        # Heart rate analysis
        if 'heart_rate' in vital_signs:
            hr = int(vital_signs['heart_rate'])
            if hr >= 120 or hr <= 50:  # Tachycardia or bradycardia
                score += 15
            elif hr >= 100 or hr <= 60:  # Elevated or low
                score += 8
        
        # Blood pressure analysis
        if 'blood_pressure' in vital_signs:
            bp = vital_signs['blood_pressure']
            if isinstance(bp, str) and '/' in bp:
                systolic, diastolic = bp.split('/')
                systolic = int(systolic)
                diastolic = int(diastolic)
                
                # Hypertensive crisis or hypotension
                if systolic >= 180 or diastolic >= 120 or systolic <= 90:
                    score += 20
                elif systolic >= 140 or diastolic >= 90 or systolic <= 100:
                    score += 10
        
        # Oxygen saturation
        if 'oxygen_saturation' in vital_signs:
            o2 = int(vital_signs['oxygen_saturation'])
            if o2 <= 90:  # Hypoxemia
                score += 25
            elif o2 <= 94:
                score += 12
        
        # Respiratory rate
        if 'respiratory_rate' in vital_signs:
            rr = int(vital_signs['respiratory_rate'])
            if rr >= 30 or rr <= 10:  # Abnormal respiratory rate
                score += 15
            elif rr >= 24 or rr <= 12:
                score += 8
        
        return min(score, 40)  # Cap at 40
    
    def _assign_priority(self, urgency_level: str, vital_signs: Dict = None) -> str:
        """
        Assign case priority based on urgency level.
        
        Returns:
            Priority level string (LOW, MEDIUM, HIGH, URGENT, CRITICAL)
        """
        if urgency_level == 'critical':
            return 'CRITICAL'
        elif urgency_level == 'high':
            return 'URGENT'
        elif urgency_level == 'moderate':
            return 'HIGH'
        elif urgency_level == 'low':
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _determine_required_agents(self, urgency_level: str, symptoms: str) -> list:
        """
        Determine which agents should be involved in the case.
        
        Returns:
            List of required agent names
        """
        agents = ['retriever', 'diagnosis']  # Always use these two
        
        # Add treatment agent for moderate and above
        if urgency_level in ['moderate', 'high', 'critical']:
            agents.append('treatment')
        
        return agents
    
    def _should_escalate_to_doctor(self, urgency_level: str, urgency_score: int) -> bool:
        """
        Decide if case should be escalated to doctor review.
        
        Returns:
            Boolean indicating if doctor review is needed
        """
        # Always escalate critical and high urgency cases
        if urgency_level in ['critical', 'high']:
            return True
        
        # Escalate moderate cases with high urgency score
        if urgency_level == 'moderate' and urgency_score >= 40:
            return True
        
        return False
    
    def _generate_routing_reason(self, urgency_level: str, urgency_score: int) -> str:
        """
        Generate human-readable reason for routing decision.
        
        Returns:
            Routing reason string
        """
        if urgency_level == 'critical':
            return f"CRITICAL urgency detected (score: {urgency_score}). Immediate doctor review required."
        elif urgency_level == 'high':
            return f"HIGH urgency detected (score: {urgency_score}). Doctor review recommended."
        elif urgency_level == 'moderate':
            return f"MODERATE urgency detected (score: {urgency_score}). Standard workflow with AI assistance."
        else:
            return f"LOW urgency detected (score: {urgency_score}). Routine case processing."
    
    def coordinate_agents(self, case, retriever_result: Dict, diagnosis_result: Dict, treatment_result: Dict = None) -> Dict:
        """
        Coordinate results from multiple agents into final recommendation.
        
        Args:
            case: Case instance
            retriever_result: Results from RetrieverAgent
            diagnosis_result: Results from DiagnosisAgent
            treatment_result: Results from TreatmentAgent (optional)
            
        Returns:
            Coordinated final decision
        """
        logger.info(f"Coordinating agent results for case #{case.id}")
        
        coordinated_result = {
            'case_id': case.id,
            'patient': f"{case.patient.first_name} {case.patient.last_name}",
            'coordination_timestamp': timezone.now().isoformat(),
            'agent_results': {
                'retriever': retriever_result,
                'diagnosis': diagnosis_result,
                'treatment': treatment_result,
            },
            'final_recommendation': self._create_final_recommendation(
                diagnosis_result, treatment_result
            ),
            'confidence_score': self._calculate_overall_confidence(
                diagnosis_result, treatment_result
            ),
        }
        
        return coordinated_result
    
    def _create_final_recommendation(self, diagnosis_result: Dict, treatment_result: Dict = None) -> str:
        """Create final coordinated recommendation."""
        recommendation = "## AI-Coordinated Medical Recommendation\n\n"
        
        if diagnosis_result:
            recommendation += f"**Primary Diagnosis:** {diagnosis_result.get('primary_diagnosis', 'Unknown')}\n\n"
        
        if treatment_result:
            recommendation += f"**Recommended Action:** {treatment_result.get('primary_action', 'Consult physician')}\n\n"
        
        return recommendation
    
    def _calculate_overall_confidence(self, diagnosis_result: Dict, treatment_result: Dict = None) -> float:
        """Calculate overall confidence score from agent results."""
        scores = []
        
        if diagnosis_result and 'confidence' in diagnosis_result:
            scores.append(diagnosis_result['confidence'])
        
        if treatment_result and 'confidence' in treatment_result:
            scores.append(treatment_result['confidence'])
        
        return sum(scores) / len(scores) if scores else 0.5
