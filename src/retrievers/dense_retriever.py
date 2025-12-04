from typing import List, Dict
import numpy as np
import os


class DenseRetriever:
    """Dense retriever using semantic embeddings"""
    
    def __init__(self, documents: List[Dict[str, str]]):
        """
        Initialize dense retriever
        
        Args:
            documents: List of documents with 'id' and 'content' keys
        """
        self.documents = documents
        
        try:
            from openai import OpenAI
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url='https://ai-gateway.andrew.cmu.edu/'
            )
            self.embedding_model = "azure/text-embedding-3-small"
            
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        print("Computing document embeddings...")
        self._compute_document_embeddings()
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text using OpenAI API
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        max_chars = 32000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            return np.array(embedding)
        
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return np.zeros(1536) 
    
    def _compute_document_embeddings(self):
        """Precompute embeddings for all documents"""
        self.doc_embeddings = []
        
        for doc in self.documents:
            embedding = self._get_embedding(doc['content'])
            self.doc_embeddings.append(embedding)
        
        self.doc_embeddings = np.array(self.doc_embeddings)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k documents for a query
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of documents with scores
        """
        query_embedding = self._get_embedding(query)
       
        similarities = []
        for doc_idx, doc_embedding in enumerate(self.doc_embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((doc_idx, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_idx, similarity in similarities[:top_k]:
            doc = self.documents[doc_idx].copy()
            doc['score'] = float(similarity)
            results.append(doc)
        
        return results