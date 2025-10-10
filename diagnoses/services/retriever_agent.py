"""
RETRIEVER AGENT - 📚 Medical Knowledge Base Search

RESPONSIBILITIES:
- Search FAISS vector database for relevant medical protocols
- Retrieve diagnostic guidelines from loaded WHO/ESPGHAN documents
- Find treatment recommendations from medical literature
- Provide evidence-based medical references
- Access 11 loaded medical documents (949,776 words)
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RetrieverAgent:
    """
    Retriever Agent searches medical knowledge base and provides evidence-based references.
    Integrates with FAISS vector database for semantic search across loaded medical documents.
    """
    
    def __init__(self):
        """Initialize the Retriever Agent."""
        self.name = "Retriever Agent"
        logger.info(f"{self.name} initialized with RAG capabilities")
    
    def search_protocols(self, query: str, symptoms: List[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Search medical protocols and diagnostic guidelines from loaded documents.
        
        Args:
            query: Search query (symptoms, condition, etc.)
            symptoms: Optional list of symptoms for more specific search
            top_k: Number of top results to return
            
        Returns:
            Dict containing search results from actual medical documents
        """
        logger.info(f"Searching protocols for query: '{query[:50]}...'")
        
        try:
            # Import RAG utilities
            from knowledge.rag_utils import search_medical_knowledge
            
            # Build comprehensive query
            if symptoms:
                symptom_text = ", ".join(symptoms)
                full_query = f"{query}. Symptoms: {symptom_text}"
            else:
                full_query = query
            
            # Search the knowledge base using RAG
            rag_results = search_medical_knowledge(full_query, top_k=top_k)
            
            # Format results with source attribution
            formatted_results = []
            sources = set()
            
            for result in rag_results:
                formatted_results.append({
                    'content': result.get('content', ''),
                    'source': result.get('source', 'Unknown'),
                    'relevance_score': result.get('score', 0.0),
                    'document_type': result.get('document_type', 'Unknown')
                })
                sources.add(result.get('source', 'Unknown'))
            
            results = {
                'query': query,
                'results': formatted_results,
                'total_found': len(formatted_results),
                'sources': list(sources),
                'knowledge_base_used': True
            }
            
            logger.info(f"Found {len(formatted_results)} relevant passages from {len(sources)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching protocols: {e}")
            return {
                'query': query,
                'results': [],
                'total_found': 0,
                'sources': [],
                'error': str(e),
                'knowledge_base_used': False
            }
    
    def retrieve_emergency_procedures(self, condition: str) -> Dict[str, Any]:
        """
        Retrieve emergency procedures for specific conditions.
        
        Args:
            condition: Medical condition or emergency type
            
        Returns:
            Dict containing emergency procedures and protocols
        """
        logger.info(f"Retrieving emergency procedures for: {condition}")
        
        # Construct emergency-focused query
        emergency_query = f"emergency treatment protocol for {condition} immediate action steps"
        
        results = self.search_protocols(emergency_query, top_k=3)
        
        # Format as emergency procedures
        procedures = {
            'condition': condition,
            'emergency_level': self._assess_emergency_level(condition),
            'immediate_actions': self._extract_action_steps(results),
            'protocols': results.get('results', []),
            'sources': results.get('sources', []),
            'warnings': self._extract_warnings(results),
        }
        
        return procedures
    
    def retrieve_cardiac_emergency_protocol(self) -> Dict[str, Any]:
        """
        Retrieve specific cardiac emergency protocols.
        
        Returns:
            Dict containing cardiac emergency procedures
        """
        logger.info("Retrieving cardiac emergency protocols")
        
        cardiac_query = "cardiac arrest heart attack emergency CPR defibrillation immediate treatment protocol"
        
        results = self.search_protocols(cardiac_query, top_k=5)
        
        cardiac_protocol = {
            'protocol_type': 'Cardiac Emergency',
            'immediate_actions': [
                "1. Call emergency services (911/ambulance) immediately",
                "2. Check patient responsiveness and breathing",
                "3. Begin CPR if patient is unresponsive and not breathing normally",
                "4. Use AED (Automated External Defibrillator) if available",
                "5. Continue CPR until emergency services arrive"
            ],
            'cpr_steps': [
                "Place patient on firm, flat surface",
                "Position hands on center of chest",
                "Compress chest at least 2 inches deep",
                "Perform 30 chest compressions at rate of 100-120/min",
                "Give 2 rescue breaths",
                "Continue 30:2 cycle until help arrives"
            ],
            'warning_signs': [
                "Chest pain or discomfort",
                "Shortness of breath",
                "Pain in arms, back, neck, jaw, or stomach",
                "Cold sweat, nausea, or lightheadedness"
            ],
            'knowledge_base_references': results.get('results', []),
            'sources': results.get('sources', [])
        }
        
        return cardiac_protocol
    
    def find_similar_cases(self, symptoms: str, patient_history: str = "", top_k: int = 3) -> Dict[str, Any]:
        """
        Find similar historical cases based on symptoms.
        
        Args:
            symptoms: Patient symptoms description
            patient_history: Patient medical history
            top_k: Number of similar cases to return
            
        Returns:
            Dict containing similar cases and patterns
        """
        logger.info(f"Finding similar cases for symptoms: '{symptoms[:50]}...'")
        
        # Combine symptoms and history for better matching
        query = f"{symptoms} {patient_history}".strip()
        
        # Search for similar case patterns
        results = self.search_protocols(query, top_k=top_k)
        
        similar_cases = {
            'query_symptoms': symptoms,
            'similar_patterns': results.get('results', []),
            'total_similar': results.get('total_found', 0),
            'pattern_insights': self._extract_pattern_insights(results),
            'common_diagnoses': self._extract_common_diagnoses(results),
        }
        
        return similar_cases
    
    def get_evidence_based_references(self, diagnosis: str, treatment: str = "") -> List[Dict]:
        """
        Get evidence-based medical references for diagnosis/treatment.
        
        Args:
            diagnosis: Proposed diagnosis
            treatment: Proposed treatment (optional)
            
        Returns:
            List of evidence-based references
        """
        logger.info(f"Getting evidence-based references for: {diagnosis}")
        
        query = f"{diagnosis} evidence-based treatment guidelines clinical recommendations"
        if treatment:
            query += f" {treatment}"
        
        results = self.search_protocols(query, top_k=5)
        
        references = []
        for result in results.get('results', []):
            reference = {
                'title': self._extract_title(result),
                'content': result.get('content', ''),
                'source': result.get('metadata', {}).get('source', 'Unknown'),
                'relevance': result.get('relevance_score', 0.0),
                'guidelines': self._extract_guidelines(result)
            }
            references.append(reference)
        
        return references
    
    def _extract_sources(self, documents: List) -> List[str]:
        """Extract unique sources from documents."""
        sources = set()
        for doc in documents:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
        return list(sources)
    
    def _extract_action_steps(self, results: Dict) -> List[str]:
        """Extract action steps from search results."""
        action_steps = []
        for result in results.get('results', []):
            content = result.get('content', '')
            # Look for numbered steps or action items
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    action_steps.append(line)
        
        return action_steps[:10]  # Return top 10 action steps
    
    def _extract_warnings(self, results: Dict) -> List[str]:
        """Extract warnings and contraindications from results."""
        warnings = []
        warning_keywords = ['warning', 'caution', 'contraindication', 'avoid', 'do not']
        
        for result in results.get('results', []):
            content = result.get('content', '').lower()
            for keyword in warning_keywords:
                if keyword in content:
                    # Extract sentence containing warning
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence:
                            warnings.append(sentence.strip().capitalize())
        
        return warnings[:5]  # Return top 5 warnings
    
    def _assess_emergency_level(self, condition: str) -> str:
        """Assess emergency level of condition."""
        critical_conditions = ['cardiac arrest', 'heart attack', 'stroke', 'anaphylaxis', 'severe bleeding']
        urgent_conditions = ['chest pain', 'difficulty breathing', 'severe pain', 'high fever']
        
        condition_lower = condition.lower()
        
        for critical in critical_conditions:
            if critical in condition_lower:
                return 'CRITICAL'
        
        for urgent in urgent_conditions:
            if urgent in condition_lower:
                return 'URGENT'
        
        return 'MODERATE'
    
    def _extract_pattern_insights(self, results: Dict) -> List[str]:
        """Extract pattern insights from similar cases."""
        insights = []
        for result in results.get('results', []):
            content = result.get('content', '')
            # Extract key insights (first sentence of each result)
            sentences = content.split('.')
            if sentences:
                insights.append(sentences[0].strip())
        
        return insights[:5]
    
    def _extract_common_diagnoses(self, results: Dict) -> List[str]:
        """Extract common diagnoses from similar cases."""
        diagnoses = []
        diagnosis_keywords = ['diagnosis:', 'diagnosed with', 'likely', 'suggests', 'indicates']
        
        for result in results.get('results', []):
            content = result.get('content', '').lower()
            for keyword in diagnosis_keywords:
                if keyword in content:
                    # Extract diagnosis mention
                    start = content.find(keyword)
                    end = content.find('.', start)
                    if end > start:
                        diagnosis = content[start:end].strip()
                        diagnoses.append(diagnosis)
        
        return list(set(diagnoses))[:5]  # Return unique diagnoses
    
    def _extract_title(self, result: Dict) -> str:
        """Extract title from result."""
        metadata = result.get('metadata', {})
        if 'title' in metadata:
            return metadata['title']
        
        # Use first line of content as title
        content = result.get('content', '')
        first_line = content.split('\n')[0]
        return first_line[:100] if first_line else 'Medical Reference'
    
    def _extract_guidelines(self, result: Dict) -> List[str]:
        """Extract treatment guidelines from result."""
        guidelines = []
        content = result.get('content', '')
        
        # Look for guideline indicators
        guideline_keywords = ['recommend', 'should', 'guideline', 'standard', 'protocol']
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in guideline_keywords):
                guidelines.append(sentence.strip())
        
        return guidelines[:3]  # Return top 3 guidelines
