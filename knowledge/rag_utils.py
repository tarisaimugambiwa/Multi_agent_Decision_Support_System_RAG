import os
import numpy as np
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import json

# Lazy-load embedding model to avoid network calls at import time
embedding_model = None
vector_store = None
document_metadata = {}  # Store document tags and metadata

def get_embedding_model():
    """Get or initialize the embedding model (lazy loading)"""
    global embedding_model
    if embedding_model is None:
        # Use local_files_only to prevent network downloads during server startup
        embedding_model = HuggingFaceEmbeddings(
            model_name='all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return embedding_model

def load_knowledge_base():
    """Load the FAISS knowledge base if it exists"""
    global vector_store
    try:
        if os.path.exists('knowledge/faiss_index.faiss') and os.path.exists('knowledge/faiss_index.pkl'):
            import faiss
            import pickle
            
            # Load FAISS index
            index = faiss.read_index('knowledge/faiss_index.faiss')
            
            # Load texts and metadata
            with open('knowledge/faiss_index.pkl', 'rb') as f:
                data = pickle.load(f)
                # Handle old format (just texts) or new format (dict with texts and metadata)
                if isinstance(data, dict):
                    texts = data.get('texts', [])
                    metadata = data.get('metadata', {})
                else:
                    texts = data  # Old format
                    metadata = {}
            
            # Create vector store wrapper
            class SimpleVectorStore:
                def __init__(self, index, texts, embeddings_model, metadata=None):
                    self.index = index
                    self.texts = texts
                    self.embeddings_model = embeddings_model
                    self.metadata = metadata or {}  # Store metadata for each chunk
                
                def similarity_search(self, query, k=5, filter_tags=None):
                    # Get query embedding
                    query_embedding = self.embeddings_model.embed_query(query)
                    
                    # Convert to numpy array if needed
                    import numpy as np
                    if not isinstance(query_embedding, np.ndarray):
                        query_embedding = np.array([query_embedding])
                    else:
                        query_embedding = query_embedding.reshape(1, -1)
                    
                    # Search in FAISS (get more results if filtering)
                    search_k = k * 3 if filter_tags else k
                    distances, indices = self.index.search(query_embedding.astype('float32'), min(search_k, len(self.texts)))
                    
                    # Return results as Document-like objects
                    results = []
                    for i, idx in enumerate(indices[0]):
                        if idx < len(self.texts):
                            # Check tag filter if specified
                            if filter_tags:
                                chunk_meta = self.metadata.get(idx, {})
                                chunk_tags = chunk_meta.get('tags', [])
                                # Skip if no matching tags
                                if not any(tag in chunk_tags for tag in filter_tags):
                                    continue
                            
                            doc = type('Doc', (), {
                                'page_content': self.texts[idx],
                                'metadata': self.metadata.get(idx, {})
                            })()
                            results.append(doc)
                            
                            # Stop when we have enough results
                            if len(results) >= k:
                                break
                    
                    return results
                
                def save_local(self, path):
                    os.makedirs('knowledge', exist_ok=True)
                    faiss.write_index(self.index, f'{path}.faiss')
                    # Save texts and metadata
                    import pickle
                    with open(f'{path}.pkl', 'wb') as f:
                        pickle.dump({'texts': self.texts, 'metadata': self.metadata}, f)
            
            vector_store = SimpleVectorStore(index, texts, get_embedding_model(), metadata)
            print("Knowledge base loaded successfully!")
            return True
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
    return False

def extract_text_from_file(file_path):
    """Extract text from various file types"""
    try:
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
                
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
            
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        else:
            print(f"Unsupported file type: {file_path}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Document tagging configuration
DOCUMENT_TAGS = {
    # Diagnosis documents
    'pneumonia': ['diagnosis', 'respiratory'],
    'malaria': ['diagnosis', 'infectious'],
    'typhoid': ['diagnosis', 'infectious'],
    'tuberculosis': ['diagnosis', 'respiratory', 'infectious'],
    'measles': ['diagnosis', 'infectious', 'pediatric'],
    'diarrhea': ['diagnosis', 'gastrointestinal', 'pediatric'],
    'meningitis': ['diagnosis', 'neurological'],
    'hiv': ['diagnosis', 'infectious'],
    'diabetes': ['diagnosis', 'metabolic'],
    
    # Treatment documents
    'treatment': ['treatment', 'management'],
    'medicine': ['treatment', 'medication'],
    'essential': ['treatment', 'medication'],
    'therapy': ['treatment'],
    'drug': ['treatment', 'medication'],
    'prescription': ['treatment', 'medication'],
    'management': ['treatment'],
    'protocol': ['treatment', 'diagnosis'],
    
    # General/Reference
    'guideline': ['diagnosis', 'treatment'],
    'who': ['diagnosis', 'treatment'],
    'espghan': ['diagnosis', 'treatment'],
    'imci': ['diagnosis', 'treatment', 'pediatric']
}

def auto_tag_document(filename, content):
    """Automatically tag document based on filename and content"""
    tags = set()
    filename_lower = filename.lower()
    content_lower = content[:1000].lower()  # Check first 1000 chars
    
    # Check filename and content against tag keywords
    for keyword, keyword_tags in DOCUMENT_TAGS.items():
        if keyword in filename_lower or keyword in content_lower:
            tags.update(keyword_tags)
    
    # Default to both if unclear
    if not tags:
        tags = {'diagnosis', 'treatment'}
    
    return list(tags)

def process_all_documents():
    """Process all documents in the sample_documents folder"""
    global vector_store
    
    sample_docs_path = 'sample_documents'
    if not os.path.exists(sample_docs_path):
        print("sample_documents folder not found!")
        return
    
    all_chunks = []
    chunk_metadata = {}  # Store metadata for each chunk
    chunk_idx = 0
    documents_processed = 0
    
    for filename in os.listdir(sample_docs_path):
        file_path = os.path.join(sample_docs_path, filename)
        
        if os.path.isfile(file_path):
            print(f"Processing: {filename}")
            text = extract_text_from_file(file_path)
            
            if text and len(text.strip()) > 0:
                # Auto-tag document
                doc_tags = auto_tag_document(filename, text)
                print(f"  - Tags: {', '.join(doc_tags)}")
                
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=512,
                    chunk_overlap=50
                )
                chunks = text_splitter.split_text(text)
                
                # Add chunks with metadata
                for chunk in chunks:
                    all_chunks.append(chunk)
                    chunk_metadata[chunk_idx] = {
                        'source': filename,
                        'tags': doc_tags
                    }
                    chunk_idx += 1
                
                documents_processed += 1
                print(f"  - Added {len(chunks)} chunks from {filename}")
            else:
                print(f"  - No text extracted from {filename}")
    
    if all_chunks:
        try:
            # Create embeddings manually
            print("Creating embeddings...")
            embeddings = get_embedding_model().embed_documents(all_chunks)
            
            # Convert to numpy array if needed
            import numpy as np
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)
            
            # Create FAISS index manually
            import faiss
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            
            # Create a simple vector store wrapper
            class SimpleVectorStore:
                def __init__(self, index, texts, embeddings_model, metadata=None):
                    self.index = index
                    self.texts = texts
                    self.embeddings_model = embeddings_model
                    self.metadata = metadata or {}
                
                def similarity_search(self, query, k=5, filter_tags=None):
                    # Get query embedding
                    query_embedding = self.embeddings_model.embed_query(query)
                    
                    # Convert to numpy array if needed
                    import numpy as np
                    if not isinstance(query_embedding, np.ndarray):
                        query_embedding = np.array([query_embedding])
                    else:
                        query_embedding = query_embedding.reshape(1, -1)
                    
                    # Search in FAISS (get more results if filtering)
                    search_k = k * 3 if filter_tags else k
                    distances, indices = self.index.search(query_embedding.astype('float32'), min(search_k, len(self.texts)))
                    
                    # Return results as Document-like objects
                    results = []
                    for i, idx in enumerate(indices[0]):
                        if idx < len(self.texts):
                            # Check tag filter if specified
                            if filter_tags:
                                chunk_meta = self.metadata.get(idx, {})
                                chunk_tags = chunk_meta.get('tags', [])
                                # Skip if no matching tags
                                if not any(tag in chunk_tags for tag in filter_tags):
                                    continue
                            
                            doc = type('Doc', (), {
                                'page_content': self.texts[idx],
                                'metadata': self.metadata.get(idx, {})
                            })()
                            results.append(doc)
                            
                            # Stop when we have enough results
                            if len(results) >= k:
                                break
                    
                    return results
                
                def save_local(self, path):
                    os.makedirs('knowledge', exist_ok=True)
                    faiss.write_index(self.index, f'{path}.faiss')
                    # Save texts and metadata
                    import pickle
                    with open(f'{path}.pkl', 'wb') as f:
                        pickle.dump({'texts': self.texts, 'metadata': self.metadata}, f)
            
            vector_store = SimpleVectorStore(index, all_chunks, get_embedding_model(), chunk_metadata)
            vector_store.save_local('knowledge/faiss_index')
            
            print(f"\n✅ Successfully processed {documents_processed} documents!")
            print(f"✅ Total chunks in knowledge base: {len(all_chunks)}")
            
        except Exception as e:
            print(f"Error creating vector store: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No documents were processed!")

def query_knowledge_base(question, top_k=5):
    """Query the knowledge base for relevant information"""
    global vector_store
    if vector_store is None:
        if not load_knowledge_base():
            return []
    
    # Search for similar documents
    results = vector_store.similarity_search(question, k=top_k)
    
    # Get actual document sources from database
    try:
        from knowledge.models import KnowledgeDocument
        all_docs = list(KnowledgeDocument.objects.all())
        
        # Create a mapping of content snippets to documents
        doc_sources = {}
        for doc in all_docs:
            # Use title or source as the identifier
            doc_sources[doc.title] = doc.source or doc.title
    except Exception as e:
        print(f"Error loading document sources: {e}")
        doc_sources = {}
    
    # Format results as list of dictionaries with actual sources
    formatted_results = []
    for i, doc in enumerate(results):
        content = doc.page_content
        
        # Try to match content to actual document
        matched_source = None
        for title, source in doc_sources.items():
            # Check if any part of the title appears in the content
            if len(title) > 20:  # Only check meaningful titles
                title_words = set(title.lower().split())
                content_words = set(content.lower().split())
                # If more than 30% of title words appear in content, it's likely a match
                overlap = len(title_words & content_words)
                if overlap > len(title_words) * 0.3:
                    matched_source = source
                    break
        
        # Fallback to generic source if no match found
        if not matched_source:
            # Use the first few document sources as fallback
            if i < len(doc_sources):
                matched_source = list(doc_sources.values())[i % len(doc_sources)]
            else:
                matched_source = 'Medical Guidelines'
        
        formatted_results.append({
            'content': content,
            'text': content,  # Keep for backwards compatibility
            'score': 1.0 - (i * 0.1),  # Approximate relevance score
            'source': matched_source
        })
    
    return formatted_results

def get_knowledge_base_stats():
    """Get statistics about the knowledge base"""
    global vector_store
    if vector_store is None:
        if not load_knowledge_base():
            return "Knowledge base not initialized"
    
    try:
        # Get approximate number of documents
        index = vector_store.index
        if hasattr(index, 'ntotal'):
            doc_count = index.ntotal
        else:
            doc_count = "Unknown"
        
        return f"Knowledge Base Stats:\n- Documents: {doc_count}\n- Index Path: knowledge/faiss_index"
    except:
        return "Knowledge base stats unavailable"


def search_medical_knowledge(query: str, top_k: int = 5, filter_tags: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search medical knowledge base for relevant information
    
    Args:
        query: The search query
        top_k: Number of results to return
        filter_tags: Optional list of tags to filter by (e.g., ['diagnosis'], ['treatment'])
        
    Returns:
        List of dictionaries with 'content', 'score', 'source', and 'tags' keys
    """
    global vector_store
    if vector_store is None:
        if not load_knowledge_base():
            return []
    
    # Search with tag filtering
    results = vector_store.similarity_search(query, k=top_k, filter_tags=filter_tags)
    
    # Format results
    formatted_results = []
    for i, doc in enumerate(results):
        formatted_results.append({
            'content': doc.page_content,
            'text': doc.page_content,
            'score': 1.0 - (i * 0.1),
            'source': getattr(doc, 'metadata', {}).get('source', 'Medical Guidelines'),
            'tags': getattr(doc, 'metadata', {}).get('tags', [])
        })
    
    return formatted_results


def search_diagnosis_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search ONLY diagnosis-related documents
    
    Args:
        query: The search query
        top_k: Number of results to return
        
    Returns:
        List of diagnosis-related documents
    """
    return search_medical_knowledge(query, top_k, filter_tags=['diagnosis'])


def search_treatment_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search ONLY treatment-related documents
    
    Args:
        query: The search query
        top_k: Number of results to return
        
    Returns:
        List of treatment-related documents
    """
    return search_medical_knowledge(query, top_k, filter_tags=['treatment'])


def get_treatment_recommendations(diagnosis: str, symptoms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Get treatment recommendations for a specific diagnosis
    
    Args:
        diagnosis: The diagnosis to search for
        symptoms: List of symptoms
        top_k: Number of results to return
        
    Returns:
        List of treatment recommendations
    """
    # Build comprehensive query
    symptom_text = ", ".join(symptoms) if symptoms else ""
    query = f"Treatment guidelines and recommendations for {diagnosis}. Patient symptoms: {symptom_text}. What are the standard treatment protocols, medications, and management approaches?"
    
    # Use treatment-filtered search
    results = search_treatment_knowledge(query, top_k)
    
    # Add treatment-specific metadata
    for result in results:
        result['type'] = 'treatment'
        result['diagnosis'] = diagnosis
    
    return results


def get_diagnostic_guidelines(symptoms: List[str], patient_info: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Get diagnostic guidelines based on symptoms and patient information
    
    Args:
        symptoms: List of symptoms
        patient_info: Optional patient information (age, sex, history, etc.)
        top_k: Number of results to return
        
    Returns:
        List of diagnostic guidelines
    """
    # Build comprehensive query
    symptom_text = ", ".join(symptoms) if symptoms else ""
    
    # Add patient context if available
    patient_context = ""
    if patient_info:
        age = patient_info.get('age', '')
        sex = patient_info.get('sex', '')
        if age:
            patient_context += f" Age: {age}."
        if sex:
            patient_context += f" Sex: {sex}."
    
    query = f"Diagnostic criteria and clinical guidelines for patient presenting with: {symptom_text}.{patient_context} What are the differential diagnoses, diagnostic criteria, and recommended investigations?"
    
    results = query_knowledge_base(query, top_k)
    
    # Add diagnostic-specific metadata
    for result in results:
        result['type'] = 'diagnostic'
        result['symptoms'] = symptoms
    
    return results