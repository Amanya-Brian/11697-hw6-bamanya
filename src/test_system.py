#!/usr/bin/env python3
"""
Test script to validate RAG system components
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from retrievers.bm25_retriever import BM25Retriever
from generators.gpt_generator import GPTGenerator
from generators.llama_generator import LlamaGenerator
from utils.data_loader import load_questions, load_corpus


def test_bm25_retriever():
    """Test BM25 retriever"""
    print("Testing BM25 Retriever...")
    
    # Create sample documents
    documents = [
        {
            'id': '0',
            'filename': 'doc1.txt',
            'content': 'Argentina won the 1986 World Cup. Diego Maradona was the captain.'
        },
        {
            'id': '1', 
            'filename': 'doc2.txt',
            'content': 'FIFA was founded in 1904. It is based in Zurich, Switzerland.'
        },
        {
            'id': '2',
            'filename': 'doc3.txt',
            'content': 'Lionel Messi plays for Inter Miami. He won the 2022 World Cup with Argentina.'
        }
    ]
    
    # Initialize retriever
    retriever = BM25Retriever(documents)
    
    # Test query
    query = "Who won the 1986 World Cup?"
    results = retriever.retrieve(query, top_k=2)
    
    print(f"Query: {query}")
    print(f"Top {len(results)} results:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. Score: {doc['score']:.3f} - {doc['content'][:80]}...")
    
    print("✓ BM25 Retriever test passed!\n")


def test_data_loader():
    """Test data loading"""
    print("Testing Data Loader...")
    
    # Create temporary test files
    os.makedirs('test_data', exist_ok=True)
    
    # Create test question file
    with open('test_data/test_questions.tsv', 'w') as f:
        f.write("Who won the 1986 World Cup?\tfactoid\n")
        f.write("List all FIFA World Cup winners\tlist\n")
    
    # Load questions
    questions, qtypes = load_questions('test_data/test_questions.tsv')
    
    assert len(questions) == 2
    assert len(qtypes) == 2
    assert qtypes[0] == 'factoid'
    assert qtypes[1] == 'list'
    
    print(f"Loaded {len(questions)} questions")
    print("✓ Data Loader test passed!\n")
    
    # Cleanup
    os.remove('test_data/test_questions.tsv')
    os.rmdir('test_data')


def test_generators():
    """Test generators availability"""
    print("Testing Generators...")
    
    # Test GPT (will fail if no API key, which is ok)
    print("  Checking GPT generator...")
    try:
        gpt = GPTGenerator()
        print("  ✓ GPT generator initialized")
    except Exception as e:
        print(f"  ⚠ GPT generator failed (expected if no API key): {e}")
    
    # Test Llama (will fail if no model, which is ok)
    print("  Checking Llama generator...")
    try:
        llama = LlamaGenerator()
        print("  ✓ Llama generator initialized")
    except Exception as e:
        print(f"  ⚠ Llama generator failed (expected if model not available): {e}")
    
    print()


def main():
    """Run all tests"""
    print("="*60)
    print("RAG System Component Tests")
    print("="*60)
    print()
    
    try:
        test_bm25_retriever()
        test_data_loader()
        test_generators()
        
        print("="*60)
        print("All basic tests passed!")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Place your data in data/ directory")
        print("3. Run: python src/rag_system.py --retriever bm25 --generator gpt")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()