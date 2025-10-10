import os
import numpy as np
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import json

# Initialize the embedding model - using HuggingFaceEmbeddings for FAISS compatibility
embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
vector_store = None

def load_knowledge_base():
    """Load the FAISS knowledge base if it exists"""
    global vector_store
    try:
        if os.path.exists('knowledge/faiss_index.faiss') and os.path.exists('knowledge/faiss_index.pkl'):
            import faiss
            import pickle
            
            # Load FAISS index
            index = faiss.read_index('knowledge/faiss_index.faiss')
            
            # Load texts
            with open('knowledge/faiss_index.pkl', 'rb') as f:
                texts = pickle.load(f)
            
            # Create vector store wrapper
            class SimpleVectorStore:
                def __init__(self, index, texts, embeddings_model):
                    self.index = index
                    self.texts = texts
                    self.embeddings_model = embeddings_model
                
                def similarity_search(self, query, k=5):
                    # Get query embedding
                    query_embedding = self.embeddings_model.embed_query(query)
                    
                    # Convert to numpy array if needed
                    import numpy as np
                    if not isinstance(query_embedding, np.ndarray):
                        query_embedding = np.array([query_embedding])
                    else:
                        query_embedding = query_embedding.reshape(1, -1)
                    
                    # Search in FAISS
                    distances, indices = self.index.search(query_embedding.astype('float32'), k)
                    
                    # Return results as Document-like objects
                    results = []
                    for i, idx in enumerate(indices[0]):
                        if idx < len(self.texts):
                            results.append(type('Doc', (), {'page_content': self.texts[idx]})())
                    
                    return results
                
                def save_local(self, path):
                    os.makedirs('knowledge', exist_ok=True)
                    faiss.write_index(self.index, f'{path}.faiss')
                    # Save texts
                    import pickle
                    with open(f'{path}.pkl', 'wb') as f:
                        pickle.dump(self.texts, f)
            
            vector_store = SimpleVectorStore(index, texts, embedding_model)
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

def process_all_documents():
    """Process all documents in the sample_documents folder"""
    global vector_store
    
    sample_docs_path = 'sample_documents'
    if not os.path.exists(sample_docs_path):
        print("sample_documents folder not found!")
        return
    
    all_chunks = []
    documents_processed = 0
    
    for filename in os.listdir(sample_docs_path):
        file_path = os.path.join(sample_docs_path, filename)
        
        if os.path.isfile(file_path):
            print(f"Processing: {filename}")
            text = extract_text_from_file(file_path)
            
            if text and len(text.strip()) > 0:
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=512,
                    chunk_overlap=50
                )
                chunks = text_splitter.split_text(text)
                all_chunks.extend(chunks)
                documents_processed += 1
                print(f"  - Added {len(chunks)} chunks from {filename}")
            else:
                print(f"  - No text extracted from {filename}")
    
    if all_chunks:
        try:
            # Create embeddings manually
            print("Creating embeddings...")
            embeddings = embedding_model.embed_documents(all_chunks)
            
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
                def __init__(self, index, texts, embeddings_model):
                    self.index = index
                    self.texts = texts
                    self.embeddings_model = embeddings_model
                
                def similarity_search(self, query, k=5):
                    # Get query embedding
                    query_embedding = self.embeddings_model.embed_query(query)
                    
                    # Convert to numpy array if needed
                    import numpy as np
                    if not isinstance(query_embedding, np.ndarray):
                        query_embedding = np.array([query_embedding])
                    else:
                        query_embedding = query_embedding.reshape(1, -1)
                    
                    # Search in FAISS
                    distances, indices = self.index.search(query_embedding.astype('float32'), k)
                    
                    # Return results as Document-like objects
                    results = []
                    for i, idx in enumerate(indices[0]):
                        if idx < len(self.texts):
                            results.append(type('Doc', (), {'page_content': self.texts[idx]})())
                    
                    return results
                
                def save_local(self, path):
                    os.makedirs('knowledge', exist_ok=True)
                    faiss.write_index(self.index, f'{path}.faiss')
                    # Save texts
                    import pickle
                    with open(f'{path}.pkl', 'wb') as f:
                        pickle.dump(self.texts, f)
            
            vector_store = SimpleVectorStore(index, all_chunks, embedding_model)
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
    
    # Format results as list of dictionaries
    formatted_results = []
    for i, doc in enumerate(results):
        formatted_results.append({
            'text': doc.page_content,
            'score': 1.0 - (i * 0.1),  # Approximate relevance score
            'source': f'Document {i+1}'
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


def search_medical_knowledge(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search medical knowledge base for relevant information
    
    Args:
        query: The search query
        top_k: Number of results to return
        
    Returns:
        List of dictionaries with 'content' and 'score' keys
    """
    return query_knowledge_base(query, top_k)


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
    
    results = query_knowledge_base(query, top_k)
    
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