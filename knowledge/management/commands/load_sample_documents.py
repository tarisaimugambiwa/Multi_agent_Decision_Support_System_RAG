"""
Management command to load sample medical documents into the Knowledge Base
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from knowledge.models import KnowledgeDocument
from knowledge.rag_utils import extract_text_from_file
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample medical documents from sample_documents/ folder into Knowledge Base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing documents before loading',
        )

    def handle(self, *args, **options):
        # Get or create a system user for document uploads
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(role='DOCTOR').first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin or doctor user found. Please create one first.'))
            return

        # Clear existing documents if requested
        if options['clear']:
            count = KnowledgeDocument.objects.count()
            KnowledgeDocument.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing documents'))

        # Document metadata mapping
        document_metadata = {
            '2020_New_Guidelines_for_the_Diagnosis_of_Paediatric_Coeliac_Disease._ESPGHAN_Advice_Guide.pdf': {
                'title': 'ESPGHAN Guidelines for Diagnosis of Paediatric Coeliac Disease (2020)',
                'document_type': 'GUIDELINE',
                'source': 'ESPGHAN (European Society for Paediatric Gastroenterology, Hepatology and Nutrition)',
                'author': 'ESPGHAN',
            },
            '9241546441.pdf': {
                'title': 'WHO Guidelines - Medical Standards',
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
                'title': 'WHO Guidelines on Tuberculosis Care',
                'document_type': 'GUIDELINE',
                'source': 'World Health Organization',
                'author': 'WHO',
            },
            '9789241548373_eng.pdf': {
                'title': 'WHO Technical Standards for Healthcare',
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
                'title': 'WHO Guideline 170 - Clinical Standards',
                'document_type': 'GUIDELINE',
                'source': 'World Health Organization',
                'author': 'WHO',
            },
            'guidelines-pediatric-arv.pdf': {
                'title': 'Guidelines for Pediatric Antiretroviral Therapy',
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
                'title': 'Operational Guidance for Paediatric Care (Uganda)',
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

        # Path to sample documents
        sample_docs_path = 'sample_documents'
        
        if not os.path.exists(sample_docs_path):
            self.stdout.write(self.style.ERROR(f'Directory {sample_docs_path} not found!'))
            return

        # Get all PDF files
        pdf_files = [f for f in os.listdir(sample_docs_path) if f.endswith('.pdf')]
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(pdf_files)} PDF documents'))
        
        loaded_count = 0
        skipped_count = 0
        error_count = 0

        for pdf_file in pdf_files:
            file_path = os.path.join(sample_docs_path, pdf_file)
            
            # Check if document already exists
            metadata = document_metadata.get(pdf_file, {})
            title = metadata.get('title', pdf_file.replace('.pdf', '').replace('_', ' '))
            
            if KnowledgeDocument.objects.filter(title=title).exists():
                self.stdout.write(self.style.WARNING(f'  ⏭️  Skipped: {title} (already exists)'))
                skipped_count += 1
                continue
            
            try:
                self.stdout.write(f'  📄 Processing: {pdf_file}...')
                
                # Extract text from PDF
                content = extract_text_from_file(file_path)
                
                if not content or len(content.strip()) < 100:
                    self.stdout.write(self.style.WARNING(f'     ⚠️  Warning: Little/no text extracted from {pdf_file}'))
                    content = f"Medical document: {title}\n\nNote: Text extraction may be limited for this document."
                
                # Create document
                doc = KnowledgeDocument.objects.create(
                    title=title,
                    content=content[:50000],  # Limit to 50k chars for database
                    document_type=metadata.get('document_type', 'REFERENCE'),
                    source=metadata.get('source', 'Unknown'),
                    author=metadata.get('author', 'Unknown'),
                    uploaded_by=admin_user,
                )
                
                loaded_count += 1
                self.stdout.write(self.style.SUCCESS(f'     ✅ Loaded: {title}'))
                self.stdout.write(f'        Words: {len(content.split())} | Chars: {len(content)}')
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'     ❌ Error loading {pdf_file}: {str(e)}'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'📊 SUMMARY:'))
        self.stdout.write(self.style.SUCCESS(f'  ✅ Successfully loaded: {loaded_count} documents'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⏭️  Skipped (already exist): {skipped_count} documents'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  ❌ Errors: {error_count} documents'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Next steps
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📌 NEXT STEPS:'))
        self.stdout.write('  1. View documents at: http://127.0.0.1:8001/knowledge/documents/')
        self.stdout.write('  2. To enable AI search, run: python manage.py process_faiss_index')
        self.stdout.write('     (This will index documents into the FAISS vector database)')
