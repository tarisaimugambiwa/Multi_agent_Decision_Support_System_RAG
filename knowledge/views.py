from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import KnowledgeDocument
from .rag_utils import extract_text_from_file, query_knowledge_base, search_medical_knowledge
import os


def check_doctor_access(user):
    """Check if user is a doctor or admin"""
    return user.role == 'DOCTOR' or user.is_staff or user.is_superuser


@login_required
def knowledge_base_dashboard(request):
    """Knowledge base dashboard with statistics and quick actions - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    # Get statistics
    total_documents = KnowledgeDocument.objects.count()
    recent_documents = KnowledgeDocument.objects.order_by('-upload_date')[:5]
    
    # Document type breakdown
    doc_types = {}
    for choice in KnowledgeDocument.DOCUMENT_TYPE_CHOICES:
        count = KnowledgeDocument.objects.filter(document_type=choice[0]).count()
        if count > 0:
            doc_types[choice[1]] = count
    
    # Check if FAISS index exists
    faiss_exists = os.path.exists('knowledge/faiss_index.faiss')
    
    context = {
        'total_documents': total_documents,
        'recent_documents': recent_documents,
        'doc_types': doc_types,
        'faiss_exists': faiss_exists,
    }
    return render(request, 'knowledge/knowledge_base.html', context)


@login_required
def document_list(request):
    """List all knowledge documents with search and filter - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    documents = KnowledgeDocument.objects.all().order_by('-upload_date')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(source__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Filter by document type
    doc_type = request.GET.get('type', '')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 10)  # 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'doc_type': doc_type,
        'document_types': KnowledgeDocument.DOCUMENT_TYPE_CHOICES,
    }
    return render(request, 'knowledge/document_list.html', context)


@login_required
def document_detail(request, pk):
    """View detailed information about a knowledge document - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    document = get_object_or_404(KnowledgeDocument, pk=pk)
    
    # Get related documents (same type)
    related_documents = KnowledgeDocument.objects.filter(
        document_type=document.document_type
    ).exclude(pk=pk)[:5]
    
    context = {
        'document': document,
        'related_documents': related_documents,
    }
    return render(request, 'knowledge/document_detail.html', context)


@login_required
def document_upload(request):
    """Upload new knowledge documents - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        document_type = request.POST.get('document_type')
        source = request.POST.get('source', '')
        author = request.POST.get('author', '')
        
        # Handle file upload if provided
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # Save file temporarily and extract text
            try:
                from .rag_utils import extract_text_from_file
                import tempfile
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    for chunk in uploaded_file.chunks():
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name
                
                # Extract text from file
                extracted_content = extract_text_from_file(tmp_path)
                if extracted_content:
                    content = extracted_content
                    if not title:
                        title = uploaded_file.name
                
                # Clean up temp file
                os.unlink(tmp_path)
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return redirect('knowledge:document_upload')
        
        # Create document
        try:
            document = KnowledgeDocument.objects.create(
                title=title,
                content=content,
                document_type=document_type,
                source=source,
                author=author,
                uploaded_by=request.user
            )
            
            # Process document for vector store
            try:
                # Note: Individual document processing would require adding documents to FAISS
                # For now, we'll skip automatic indexing and rely on batch processing
                messages.success(request, f'Document "{title}" uploaded successfully! Run process_all_documents() to index.')
            except Exception as e:
                messages.warning(request, f'Document uploaded but indexing skipped: {str(e)}')
            
            return redirect('knowledge:document_detail', pk=document.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating document: {str(e)}')
    
    context = {
        'document_types': KnowledgeDocument.DOCUMENT_TYPE_CHOICES,
    }
    return render(request, 'knowledge/document_upload.html', context)


@login_required
def document_delete(request, pk):
    """Delete a knowledge document - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    document = get_object_or_404(KnowledgeDocument, pk=pk)
    
    if request.method == 'POST':
        title = document.title
        try:
            document.delete()
            messages.success(request, f'Document "{title}" has been successfully deleted.')
            messages.warning(request, 'Note: You may need to rebuild the FAISS index to remove this document from search results.')
            return redirect('knowledge:document_list')
        except Exception as e:
            messages.error(request, f'Error deleting document: {str(e)}')
            return redirect('knowledge:document_detail', pk=pk)
    
    # If GET request, redirect to detail page (delete should only be POST)
    return redirect('knowledge:document_detail', pk=pk)


@login_required
def search_knowledge(request):
    """Search knowledge base using RAG - Doctor only"""
    if not check_doctor_access(request.user):
        messages.error(request, 'Access denied. Knowledge Base is only available to doctors.')
        return redirect('home')
    
    query = request.GET.get('q', '')
    results = []
    
    if query:
        try:
            # Use RAG to search
            rag_results = search_medical_knowledge(query, top_k=10)
            
            # Format results
            results = []
            for result in rag_results:
                results.append({
                    'content': result.get('text', result.get('content', '')),
                    'source': result.get('source', 'Unknown'),
                })
        except Exception as e:
            messages.error(request, f'Search error: {str(e)}')
    
    context = {
        'query': query,
        'results': results,
        'result_count': len(results),
    }
    return render(request, 'knowledge/search_results.html', context)
