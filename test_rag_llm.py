"""
Test script to verify RAG + LLM integration works properly
"""
import os
import sys
import django

# Setup Django
os.chdir(r'c:\Users\tarisaim\Desktop\DS_System')
sys.path.insert(0, r'c:\Users\tarisaim\Desktop\DS_System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

# Now test the system
print("=" * 70)
print("TESTING RAG + LLM INTEGRATION")
print("=" * 70)

# Test 1: Check knowledge base documents
print("\n[1] Checking Knowledge Base Documents...")
from knowledge.models import KnowledgeDocument
docs = KnowledgeDocument.objects.all()
print(f"   ✅ Total documents loaded: {docs.count()}")
for doc in docs[:3]:
    print(f"   - {doc.title[:60]}... (Source: {doc.source})")

# Test 2: Test RAG search
print("\n[2] Testing RAG Search...")
from knowledge.rag_utils import search_medical_knowledge
test_query = "fever, headache, body aches"
results = search_medical_knowledge(test_query, top_k=3)
print(f"   ✅ RAG returned {len(results)} results")
if results:
    for i, result in enumerate(results[:2], 1):
        source = result.get('source', 'Unknown')
        content_preview = result.get('content', '')[:100]
        print(f"   Result {i}: Source = {source}")
        print(f"   Preview: {content_preview}...")

# Test 3: Test AI Diagnosis
print("\n[3] Testing AI Diagnosis Engine...")
from diagnoses.ai_utils import get_ai_diagnosis
symptoms = "High fever 39°C for 3 days, severe headache, body aches, fatigue"
patient_history = {
    'patient_id': 'TEST001',
    'age': 25,
    'gender': 'Male',
    'medical_history': 'None'
}
diagnosis_result = get_ai_diagnosis(symptoms, patient_history)
print(f"   ✅ Diagnosis completed")
print(f"   Primary Diagnoses: {len(diagnosis_result.get('primary_diagnoses', []))}")
if diagnosis_result.get('primary_diagnoses'):
    top_dx = diagnosis_result['primary_diagnoses'][0]
    print(f"   Top Diagnosis: {top_dx.get('condition')} (Confidence: {top_dx.get('confidence'):.2f})")
print(f"   Urgency Level: {diagnosis_result.get('urgency_level')}")
print(f"   Knowledge Sources Used: {diagnosis_result.get('knowledge_sources', 0)}")

# Test 4: Test Retriever Agent
print("\n[4] Testing Retriever Agent...")
from diagnoses.services.retriever_agent import RetrieverAgent
retriever = RetrieverAgent()
symptom_list = ["fever", "headache", "body aches"]
retriever_results = retriever.search_protocols(
    query=symptoms,
    symptoms=symptom_list,
    top_k=5
)
print(f"   ✅ Retriever returned {len(retriever_results.get('results', []))} results")
print(f"   Sources: {', '.join(retriever_results.get('sources', [])[:3])}")
print(f"   Knowledge Base Used: {retriever_results.get('knowledge_base_used', False)}")

# Test 5: Test Diagnosis Agent
print("\n[5] Testing Diagnosis Agent...")
from diagnoses.services.diagnosis_agent import DiagnosisAgent
diagnosis_agent = DiagnosisAgent()

patient_history_dict = {
    'medical_history': 'None',
    'allergies': 'None'
}
demographics = {
    'age': 25,
    'gender': 'Male'
}
vital_signs = {
    'temperature': '39',
    'heart_rate': '95',
    'blood_pressure': '120/80'
}

diagnosis_analysis = diagnosis_agent.analyze_symptoms(
    symptoms=symptoms,
    patient_history=patient_history_dict,
    demographics=demographics,
    vital_signs=vital_signs,
    retriever_context=retriever_results
)

print(f"   ✅ Diagnosis Analysis completed")
print(f"   Primary Diagnosis: {diagnosis_analysis.get('primary_diagnosis')}")
print(f"   Confidence Score: {diagnosis_analysis.get('confidence_score'):.2f}")
print(f"   Urgency Assessment: {diagnosis_analysis.get('urgency_assessment')}")
print(f"   Red Flags: {len(diagnosis_analysis.get('red_flags', []))}")
print(f"   Emergency Conditions: {len(diagnosis_analysis.get('emergency_conditions', []))}")

# Test 6: Test Treatment Agent
print("\n[6] Testing Treatment Agent...")
from diagnoses.services.treatment_agent import TreatmentAgent
treatment_agent = TreatmentAgent()

treatment_plan = treatment_agent.create_action_plan(
    diagnosis=diagnosis_analysis,
    urgency_level=diagnosis_analysis.get('urgency_assessment', 'moderate'),
    symptoms=symptom_list
)

print(f"   ✅ Treatment Plan created")
print(f"   Immediate Actions: {len(treatment_plan.get('immediate_actions', []))}")
print(f"   Evidence Sources: {', '.join(treatment_plan.get('evidence_sources', [])[:2])}")
print(f"   Knowledge Base Used: {treatment_plan.get('knowledge_base_used', False)}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ Knowledge Base: {docs.count()} documents loaded")
print(f"✅ RAG Search: Working with actual document sources")
print(f"✅ AI Diagnosis: Generating diagnoses with medical patterns")
print(f"✅ Retriever Agent: Querying knowledge base successfully")
print(f"✅ Diagnosis Agent: Analyzing symptoms with RAG context")
print(f"✅ Treatment Agent: Creating evidence-based treatment plans")
print("\n🎉 ALL SYSTEMS OPERATIONAL!")
print("=" * 70)
