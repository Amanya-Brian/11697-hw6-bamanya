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
        
        # OpenAI client
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
        # System msg with format instructions
        format_instructions = self._get_format_instructions(question_type)
        
        if context:
            prompt = f"""You are a knowledgeable football expert assistant. Answer the question based on the provided context.

CRITICAL INSTRUCTIONS:
1. READ the question carefully
2. USE the context to inform your answer
3. ANSWER the specific question asked
4. Do NOT copy random text from the context
5. Do NOT answer a different question
6. Follow the format requirements exactly

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
            return """CRITICAL FORMAT REQUIREMENT:
- Provide ONLY a short, direct answer (1-5 words maximum)
- Do NOT include any explanation, context, or extra words
- Just the answer itself

Example:
Q: Who won the 1986 World Cup?
A: Argentina

Q: What year was FIFA founded?
A: 1904"""
        
        elif question_type == 'list':
            return """CRITICAL FORMAT REQUIREMENT:
- Provide ONLY the items separated by TABS (\\t character)
- Do NOT use commas, newlines, or any other separator
- Do NOT use numbers (1., 2., 3.) or bullet points
- Do NOT include any explanation or extra text
- Format: Item1\\tItem2\\tItem3

Example:
Q: List the three clubs Messi played for.
A: Barcelona\\tParis Saint-Germain\\tInter Miami

Q: Name all South American countries that won the World Cup.
A: Brazil\\tArgentina\\tUruguay"""
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            return """CRITICAL FORMAT REQUIREMENT:
- Provide numbered steps (1., 2., 3., etc.)
- Each step on a new line
- Be clear and concise
- Do NOT include extra explanations

Example:
Q: Describe the steps for taking a penalty kick.
A: 1. Place the ball on the penalty mark
2. Wait for the referee's signal
3. Kick the ball forward
4. Do not touch the ball again until another player touches it"""
        
        elif 'multiple choice' in question_type or question_type == 'multiple choice':
            return """CRITICAL FORMAT REQUIREMENT:
- Respond with ONLY a SINGLE LETTER: A, B, C, or D
- Do NOT include the answer text
- Do NOT include any explanation
- Do NOT include punctuation
- JUST THE LETTER

Example:
Q: Which country won the 2018 World Cup? A) France B) Croatia C) Brazil D) Germany
A: A

Q: Who scored the most goals? A) Messi B) Ronaldo C) Pele D) Mbappe
A: B"""
        
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
                temperature=0.3,  # for more consistent answers
                max_tokens=500
            )
            
            raw_answer = response.choices[0].message.content.strip()
            
            answer = self._post_process_answer(raw_answer, question_type)
            
            metadata = {
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'raw_answer': raw_answer,  # Store raw for debugging
                'question_type': question_type
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
        import re
        
        answer = answer.strip()
        question_type = question_type.lower()
        
        prefixes_to_remove = [
            "Answer:",
            "The answer is:",
            "The answer is",
            "Response:",
            "A:",
        ]
        
        for prefix in prefixes_to_remove:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix):].strip()
                if answer and answer[0] in [':', '-']:
                    answer = answer[1:].strip()
        
        # post-processing
        if 'multiple choice' in question_type or question_type == 'multiple choice':
            if answer and answer[0].upper() in 'ABCD':
                return answer[0].upper()
            
            match = re.search(r'\b([A-D])\b', answer.upper())
            if match:
                return match.group(1)
            
            match = re.search(r'(?:option|choice|answer)[\s:]?([A-D])', answer, re.IGNORECASE)
            if match:
                return match.group(1).upper()
            
            letters = [c for c in answer.upper() if c in 'ABCD']
            if len(letters) == 1:
                return letters[0]
            
            if answer and answer[0].upper() in 'ABCD':
                return answer[0].upper()
            
            return 'A' 
        
        elif question_type == 'list':
            lines = answer.split('\n')
            items = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                cleaned = re.sub(r'^\s*[\d\.\-\•\*\)]+\s*', '', line)
                cleaned = cleaned.strip()
                
                if cleaned.lower().startswith('and '):
                    cleaned = cleaned[4:].strip()
                
                if cleaned:
                    items.append(cleaned)
            
            if len(items) <= 1 and ',' in answer:
                items = [item.strip() for item in answer.split(',') if item.strip()]
                items = [re.sub(r'^\s*[\d\.\-\•\*\)]+\s*', '', item).strip() for item in items]
            
            return '\t'.join(items) if items else answer
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            lines = answer.split('\n')
            
            steps = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                line = re.sub(r'^\s*[\d\.\-\•\*]+\s*', '', line)
                line = line.strip()
                
                if line:
                    steps.append(line)
            
            if steps:
                numbered = [f"{i+1}. {step}" for i, step in enumerate(steps)]
                return '\\n'.join(numbered) 
            
            return answer
        
        return answer