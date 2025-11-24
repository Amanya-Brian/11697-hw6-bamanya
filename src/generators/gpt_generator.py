"""
GPT Generator - API-based generator using OpenAI GPT models
"""

from typing import Tuple, Dict
import os
import json


class GPTGenerator:
    """Generator using OpenAI GPT models"""
    
    def __init__(self, model: str = "gpt-4o-mini-2024-07-18"):
        """
        Initialize GPT generator
        
        Args:
            model: OpenAI model name
        """
        self.model = model
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url='https://ai-gateway.andrew.cmu.edu/'
            )
            
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
    
    def _build_prompt(
        self,
        question: str,
        question_type: str,
        context: str
    ) -> str:
        """
        Build prompt for answer generation
        
        Args:
            question: Question to answer
            question_type: Type of question
            context: Retrieved context documents
            
        Returns:
            Formatted prompt
        """
        format_instructions = self._get_format_instructions(question_type)
        
        if context:
            prompt = f"""You are a knowledgeable football expert assistant. Answer the question based on the provided context.

Context:
{context}

Question: {question}

{format_instructions}

Answer:"""
        else:
            prompt = f"""You are a knowledgeable football expert assistant. Answer the question using your knowledge.

Question: {question}

{format_instructions}

Answer:"""
        
        return prompt
    
    def _get_format_instructions(self, question_type: str) -> str:
        """
        Get format instructions based on question type
        
        Args:
            question_type: Type of question
            
        Returns:
            Format instructions string
        """
        question_type = question_type.lower()
        
        if question_type == 'factoid':
            return "Provide a concise, direct answer (a few words or a short phrase). Do not include explanations."
        
        elif question_type == 'list':
            return "Provide your answer as a numbered list. Each item should be on a new line starting with a number."
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            return "Provide step-by-step instructions. Number each step clearly."
        
        elif 'multiple choice' in question_type or question_type == 'multiple choice':
            return "Provide only the letter of the correct answer (A, B, C, or D). Do not include explanations."
        
        else:
            return "Provide a clear, concise answer."
    
    def generate(
        self,
        question: str,
        question_type: str,
        context: str = ""
    ) -> Tuple[str, Dict]:
        """
        Generate answer for a question
        
        Args:
            question: Question to answer
            question_type: Type of question
            context: Retrieved context (optional)
            
        Returns:
            Tuple of (answer, metadata)
        """
        # prompt
        prompt = self._build_prompt(question, question_type, context)
        
        # answer
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful football expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            # metadata
            metadata = {
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
            
            return answer, metadata
        
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "", {'error': str(e)}
    
    def _post_process_answer(self, answer: str, question_type: str) -> str:
        """
        Post-process answer based on question type
        
        Args:
            answer: Raw answer from model
            question_type: Type of question
            
        Returns:
            Post-processed answer
        """
        prefixes_to_remove = [
            "Answer:",
            "The answer is:",
            "Response:",
        ]
        
        for prefix in prefixes_to_remove:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix):].strip()
        
        return answer