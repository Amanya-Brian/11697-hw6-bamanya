#!/usr/bin/env python3
"""
RAG System for Football QA
Supports multiple retriever and generator combinations
"""

import argparse
import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Tuple, Optional
import numpy as np
from tqdm import tqdm

# Import retriever and generator modules
from retrievers.bm25_retriever import BM25Retriever
from retrievers.dense_retriever import DenseRetriever
from generators.gpt_generator import GPTGenerator
from generators.llama_generator import LlamaGenerator
from utils.data_loader import load_questions, load_corpus


class RAGSystem:
    """Main RAG system that combines retrievers and generators"""
    
    def __init__(
        self,
        retriever_type: str,
        generator_type: str,
        corpus_path: str,
        top_k: int = 3
    ):
        """
        Initialize RAG system
        
        Args:
            retriever_type: 'bm25', 'dense', or 'none'
            generator_type: 'gpt' or 'llama'
            corpus_path: Path to document corpus
            top_k: Number of documents to retrieve
        """
        self.retriever_type = retriever_type
        self.generator_type = generator_type
        self.top_k = top_k
        
        # Load corpus
        print(f"Loading corpus from {corpus_path}...")
        self.documents = load_corpus(corpus_path)
        print(f"Loaded {len(self.documents)} documents")
        
        # Initialize retriever
        if retriever_type.lower() != 'none':
            print(f"Initializing {retriever_type} retriever...")
            if retriever_type.lower() == 'bm25':
                self.retriever = BM25Retriever(self.documents)
            elif retriever_type.lower() == 'dense':
                self.retriever = DenseRetriever(self.documents)
            else:
                raise ValueError(f"Unknown retriever type: {retriever_type}")
        else:
            self.retriever = None
            print("No retriever - using direct generation")
        
        # Initialize generator
        print(f"Initializing {generator_type} generator...")
        if generator_type.lower() == 'gpt':
            self.generator = GPTGenerator()
        elif generator_type.lower() == 'llama':
            self.generator = LlamaGenerator()
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
    
    def retrieve(self, query: str) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Question to retrieve documents for
            
        Returns:
            List of retrieved documents with scores
        """
        if self.retriever is None:
            return []
        
        return self.retriever.retrieve(query, top_k=self.top_k)
    
    def generate(
        self,
        question: str,
        question_type: str,
        retrieved_docs: List[Dict]
    ) -> Tuple[str, Dict]:
        """
        Generate answer given question and retrieved documents
        
        Args:
            question: Question to answer
            question_type: Type of question (factoid, list, etc.)
            retrieved_docs: Retrieved documents to use as context
            
        Returns:
            Tuple of (answer, metadata)
        """
        # Build context from retrieved documents
        context = ""
        if retrieved_docs:
            context = "\n\n".join([
                f"Document {i+1}:\n{doc['content']}"
                for i, doc in enumerate(retrieved_docs)
            ])
        
        # Generate answer
        answer, metadata = self.generator.generate(
            question=question,
            question_type=question_type,
            context=context
        )
        
        # Add retrieval info to metadata
        if retrieved_docs:
            metadata['retrieved_doc_ids'] = [doc.get('id', '') for doc in retrieved_docs]
            metadata['retrieval_scores'] = [doc.get('score', 0.0) for doc in retrieved_docs]
        
        return answer, metadata
    
    def answer_question(
        self,
        question: str,
        question_type: str
    ) -> Tuple[str, Dict]:
        """
        Full pipeline: retrieve + generate
        
        Args:
            question: Question to answer
            question_type: Type of question
            
        Returns:
            Tuple of (answer, metadata)
        """
        # Retrieve documents
        retrieved_docs = self.retrieve(question)
        
        # Generate answer
        answer, metadata = self.generate(question, question_type, retrieved_docs)
        
        return answer, metadata


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description='RAG System for Football QA'
    )
    parser.add_argument(
        '--retriever',
        type=str,
        choices=['bm25', 'dense', 'none'],
        required=True,
        help='Retriever type: bm25, dense, or none'
    )
    parser.add_argument(
        '--generator',
        type=str,
        choices=['gpt', 'llama'],
        required=True,
        help='Generator type: gpt or llama'
    )
    parser.add_argument(
        '--questions',
        type=str,
        default='data/question.tsv',
        help='Path to questions TSV file'
    )
    parser.add_argument(
        '--corpus',
        type=str,
        default='data/corpus',
        help='Path to document corpus directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: output/prediction/<retriever>_<generator>.tsv)'
    )
    parser.add_argument(
        '--top_k',
        type=int,
        default=3,
        help='Number of documents to retrieve (default: 3)'
    )
    parser.add_argument(
        '--batch_size',
        type=int,
        default=1,
        help='Batch size for processing (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Set default output path
    if args.output is None:
        output_dir = Path('output/prediction')
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = output_dir / f"{args.retriever}_{args.generator}.tsv"
    
    # Initialize system
    print("="*80)
    print(f"RAG System Configuration:")
    print(f"  Retriever: {args.retriever}")
    print(f"  Generator: {args.generator}")
    print(f"  Top-K: {args.top_k}")
    print("="*80)
    
    system = RAGSystem(
        retriever_type=args.retriever,
        generator_type=args.generator,
        corpus_path=args.corpus,
        top_k=args.top_k
    )
    
    # Load questions
    print(f"\nLoading questions from {args.questions}...")
    questions, question_types = load_questions(args.questions)
    print(f"Loaded {len(questions)} questions")
    
    # Process questions
    print(f"\nProcessing questions...")
    results = []
    
    for i, (question, qtype) in enumerate(tqdm(
        zip(questions, question_types),
        total=len(questions),
        desc="Answering"
    )):
        try:
            answer, metadata = system.answer_question(question, qtype)
            
            # Format metadata as JSON string
            metadata_str = json.dumps(metadata)
            
            results.append({
                'question': question,
                'answer': answer,
                'metadata': metadata_str
            })
            
        except Exception as e:
            print(f"\nError processing question {i}: {question}")
            print(f"Error: {str(e)}")
            results.append({
                'question': question,
                'answer': '',
                'metadata': json.dumps({'error': str(e)})
            })
    
    # Save results
    print(f"\nSaving results to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        for result in results:
            # TSV format: answer \t metadata
            f.write(f"{result['answer']}\t{result['metadata']}\n")
    
    print(f"\nDone! Results saved to {args.output}")
    print("="*80)


if __name__ == '__main__':
    main()