"""
BM25 Retriever - Sparse retrieval using BM25 algorithm
This is an open-weight retriever (no API calls)
"""

from typing import List, Dict
import math
from collections import Counter
import re


class BM25Retriever:
    """BM25 retriever for sparse document retrieval"""
    
    def __init__(self, documents: List[Dict[str, str]], k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 retriever
        
        Args:
            documents: List of documents with 'id' and 'content' keys
            k1: BM25 k1 parameter (term frequency saturation)
            b: BM25 b parameter (length normalization)
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        
        # Preprocess and index documents
        self._build_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Convert to lowercase and split on non-alphanumeric characters
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _build_index(self):
        """Build inverted index and calculate document statistics"""
        # Tokenize all documents
        self.doc_tokens = []
        self.doc_lengths = []
        
        for doc in self.documents:
            tokens = self._tokenize(doc['content'])
            self.doc_tokens.append(tokens)
            self.doc_lengths.append(len(tokens))
        
        # Calculate average document length
        self.avgdl = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # Build inverted index: term -> list of (doc_id, term_frequency)
        self.inverted_index = {}
        
        for doc_idx, tokens in enumerate(self.doc_tokens):
            term_freqs = Counter(tokens)
            
            for term, freq in term_freqs.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((doc_idx, freq))
        
        # Calculate IDF for each term
        self.idf = {}
        N = len(self.documents)
        
        for term, postings in self.inverted_index.items():
            df = len(postings)  # document frequency
            # IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
            self.idf[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
    
    def _bm25_score(self, query_tokens: List[str], doc_idx: int) -> float:
        """
        Calculate BM25 score for a document given query tokens
        
        Args:
            query_tokens: List of query tokens
            doc_idx: Document index
            
        Returns:
            BM25 score
        """
        score = 0.0
        doc_len = self.doc_lengths[doc_idx]
        
        # Get term frequencies for this document
        doc_term_freqs = Counter(self.doc_tokens[doc_idx])
        
        for term in query_tokens:
            if term not in self.inverted_index:
                continue
            
            # Get term frequency in document
            tf = doc_term_freqs.get(term, 0)
            
            if tf == 0:
                continue
            
            # Get IDF
            idf = self.idf[term]
            
            # Calculate BM25 component for this term
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k documents for a query
        
        Args:
            query: Query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of documents with scores
        """
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Calculate scores for all documents
        scores = []
        for doc_idx in range(len(self.documents)):
            score = self._bm25_score(query_tokens, doc_idx)
            scores.append((doc_idx, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k documents
        results = []
        for doc_idx, score in scores[:top_k]:
            doc = self.documents[doc_idx].copy()
            doc['score'] = score
            results.append(doc)
        
        return results