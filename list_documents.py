#!/usr/bin/env python
"""
List all documents in the knowledge base with details
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')
django.setup()

from knowledge.models import KnowledgeDocument

docs = KnowledgeDocument.objects.all()
total_words = sum(len(doc.content.split()) for doc in docs)

print("=" * 80)
print("📚 KNOWLEDGE BASE SUMMARY")
print("=" * 80)
print(f"\nTotal Documents: {docs.count()}")
print(f"Total Words: {total_words:,}")
print(f"Average Words per Document: {total_words // docs.count():,}")
print("\n" + "=" * 80)

for i, doc in enumerate(docs, 1):
    preview = ' '.join(doc.content[:300].split())
    print(f"\n{i}. {doc.title}")
    print(f"   📑 Type: {doc.get_document_type_display()}")
    print(f"   🏥 Source: {doc.source}")
    print(f"   📊 Words: {len(doc.content.split()):,}")
    print(f"   📅 Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   👤 By: {doc.uploaded_by.username}")
    print(f"   📝 Preview: {preview}...")
    print("-" * 80)
