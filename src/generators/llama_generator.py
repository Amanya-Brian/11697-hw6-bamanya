from typing import Tuple, Dict


class LlamaGenerator:
    """Generator using Llama via Ollama"""
    
    def __init__(self, model: str = "llama3"):
        """
        Initialize Llama generator using Ollama
        
        Args:
            model: Ollama model name (e.g., "llama3", "llama3.1", "llama2")
        """
        self.model = model
        
        print(f"Initializing Ollama with model: {model}...")
        
        # Initialize Ollama
        try:
            from langchain_community.llms import Ollama
            
            self.llm = Ollama(model=model)
            
            # Test the connection
            try:
                test_response = self.llm.invoke("Hi")
                print(f"Ollama connection successful! Model: {model}")
            except Exception as e:
                print(f"Warning: Ollama test failed: {e}")
                print("Make sure Ollama is running: ollama serve")
                raise
            
        except ImportError:
            raise ImportError(
                "LangChain not installed. Install with: pip install langchain langchain-community"
            )
    
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
        # Get format instructions
        format_instructions = self._get_format_instructions(question_type)
        
        if context:
            prompt = f"""You are a knowledgeable football expert. Answer the question based on the context provided.

Context:
{context}

Question: {question}

{format_instructions}

Answer:"""
        else:
            prompt = f"""You are a knowledgeable football expert. Answer the question using your knowledge.

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
            return "Give a brief, direct answer (a few words or short phrase only). Do not add explanations."
        
        elif question_type == 'list':
            return "List your answer with numbered items (1. 2. 3. etc.)."
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            return "Provide numbered step-by-step instructions (1. 2. 3. etc.)."
        
        elif 'multiple choice' in question_type or question_type == 'multiple choice':
            return "Answer with ONLY the letter (A, B, C, or D). Nothing else."
        
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
        # Build prompt
        prompt = self._build_prompt(question, question_type, context)
        
        # Generate using Ollama
        try:
            answer = self.llm.invoke(prompt)
            
            # Post-process answer
            answer = self._post_process_answer(answer, question_type)
            
            # Metadata
            metadata = {
                'model': f'ollama/{self.model}',
                'backend': 'ollama'
            }
            
            return answer, metadata
        
        except Exception as e:
            print(f"Error generating answer with Ollama: {e}")
            return "", {'error': str(e)}
    
    def _post_process_answer(self, answer: str, question_type: str) -> str:
        """
        Post-process answer to clean it up
        
        Args:
            answer: Raw answer from model
            question_type: Type of question
            
        Returns:
            Cleaned answer
        """
        # Remove common prefixes
        prefixes = [
            "Answer:",
            "The answer is:",
            "Response:",
            "Here is the answer:",
            "Here's the answer:",
        ]
        
        for prefix in prefixes:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix):].strip()
        
        # For multiple choice, extract just the letter
        if 'multiple choice' in question_type.lower():
            import re
            # Look for pattern like "A)" or "A." or just "A" at the start
            match = re.search(r'^\s*([A-D])\b', answer)
            if match:
                answer = match.group(1)
            else:
                # Try to find it anywhere in the first line
                first_line = answer.split('\n')[0]
                match = re.search(r'\b([A-D])\b', first_line)
                if match:
                    answer = match.group(1)
        
        # Limit length for factoid questions
        if question_type.lower() == 'factoid':
            # Take only first sentence or first 50 words
            sentences = answer.split('.')
            if sentences:
                answer = sentences[0].strip()
            words = answer.split()
            if len(words) > 50:
                answer = ' '.join(words[:50])
        
        return answer.strip()