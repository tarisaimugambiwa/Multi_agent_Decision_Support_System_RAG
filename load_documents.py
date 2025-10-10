"""
Simple script to load sample documents
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from django.contrib.auth import get_user_model
from knowledge.models import KnowledgeDocument
from knowledge.rag_utils import extract_text_from_file

User = get_user_model()

print("🚀 Loading Sample Documents into Knowledge Base...")
print("=" * 60)

# Get admin user
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.filter(role='DOCTOR').first()

if not admin_user:
    print("❌ No admin or doctor user found!")
    sys.exit(1)

print(f"✅ Using user: {admin_user.username}")

# Document metadata
document_metadata = {
    '2020_New_Guidelines_for_the_Diagnosis_of_Paediatric_Coeliac_Disease._ESPGHAN_Advice_Guide.pdf': {
        'title': 'ESPGHAN Guidelines for Diagnosis of Paediatric Coeliac Disease (2020)',
        'document_type': 'GUIDELINE',
        'source': 'ESPGHAN',
        'author': 'ESPGHAN',
    },
    '9241546441.pdf': {
        'title': 'WHO Medical Standards Guidelines',
        'document_type': 'GUIDELINE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    '9241594934_eng.pdf': {
        'title': 'WHO Pocket Book of Hospital Care for Children',
        'document_type': 'MANUAL',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    '9789240033986-eng.pdf': {
        'title': 'WHO Guidelines on Tuberculosis Infection Prevention and Control',
        'document_type': 'GUIDELINE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    '9789241548373_eng.pdf': {
        'title': 'WHO Technical Standards for Medical Devices',
        'document_type': 'REFERENCE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    'B09514-eng.pdf': {
        'title': 'WHO Clinical Care Guidelines',
        'document_type': 'GUIDELINE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    'guideline-170-en.pdf': {
        'title': 'WHO Guideline 170 - Clinical Practice Standards',
        'document_type': 'GUIDELINE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
    'guidelines-pediatric-arv.pdf': {
        'title': 'Pediatric Antiretroviral Therapy Guidelines',
        'document_type': 'GUIDELINE',
        'source': 'WHO/CDC',
        'author': 'WHO',
    },
    'Standard-Treatment-Manual.pdf': {
        'title': 'Standard Treatment Manual - Essential Medicines',
        'document_type': 'MANUAL',
        'source': 'Ministry of Health',
        'author': 'National Health Authority',
    },
    'uga-ch-41-02-operational-guidance-2014-eng-paediatric-guidelines.pdf': {
        'title': 'Operational Guidance for Paediatric HIV Care (Uganda 2014)',
        'document_type': 'GUIDELINE',
        'source': 'Uganda Ministry of Health',
        'author': 'Uganda MoH',
    },
    'WHO-MHP-HPS-EML-2023.02-eng.pdf': {
        'title': 'WHO Essential Medicines List 2023',
        'document_type': 'REFERENCE',
        'source': 'World Health Organization',
        'author': 'WHO',
    },
}

sample_docs_path = 'sample_documents'
pdf_files = [f for f in os.listdir(sample_docs_path) if f.endswith('.pdf')]

print(f"\n📂 Found {len(pdf_files)} PDF files in sample_documents/")
print()

loaded = 0
skipped = 0
errors = 0

for pdf_file in pdf_files:
    file_path = os.path.join(sample_docs_path, pdf_file)
    metadata = document_metadata.get(pdf_file, {})
    title = metadata.get('title', pdf_file.replace('.pdf', '').replace('_', ' '))
    
    # Check if already exists
    if KnowledgeDocument.objects.filter(title=title).exists():
        print(f"⏭️  SKIP: {title[:60]}... (already exists)")
        skipped += 1
        continue
    
    try:
        print(f"📄 Processing: {pdf_file[:50]}...")
        
        # Extract text
        content = extract_text_from_file(file_path)
        
        if not content or len(content.strip()) < 50:
            content = f"Medical Document: {title}\n\nThis is a medical guideline/reference document."
            print(f"   ⚠️  Warning: Limited text extracted")
        
        # Create document
        doc = KnowledgeDocument.objects.create(
            title=title,
            content=content[:50000],
            document_type=metadata.get('document_type', 'REFERENCE'),
            source=metadata.get('source', 'Unknown'),
            author=metadata.get('author', 'Unknown'),
            uploaded_by=admin_user,
        )
        
        word_count = len(content.split())
        print(f"   ✅ SUCCESS: {word_count:,} words loaded")
        loaded += 1
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:100]}")
        errors += 1

# Summary
print()
print("=" * 60)
print("📊 SUMMARY:")
print(f"   ✅ Loaded: {loaded} documents")
print(f"   ⏭️  Skipped: {skipped} documents")
print(f"   ❌ Errors: {errors} documents")
print("=" * 60)
print()
print("🎉 Done! View documents at:")
print("   http://127.0.0.1:8001/knowledge/documents/")
