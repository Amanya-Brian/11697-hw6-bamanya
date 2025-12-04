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
            
            # Test connection
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
        # format instructions
        format_instructions = self._get_format_instructions(question_type)
        
        if context:
            prompt = f"""You are a knowledgeable football expert. Answer the question based on the context provided.

IMPORTANT:
1. Read the question carefully
2. Use context to find the answer
3. Answer ONLY the question asked
4. Do NOT copy random text from context
5. Follow the format requirements

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
            return """FORMAT: Short direct answer (1-5 words). No explanation.

Example: Q: Who won 1986 World Cup? A: Argentina"""
        
        elif question_type == 'list':
            return """FORMAT: Items separated by tabs (\\t). No numbers or bullets.

Example: Q: List Messi's clubs. A: Barcelona\\tPSG\\tInter Miami"""
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            return """FORMAT: Numbered steps (1. 2. 3.)

Example: Q: How to take penalty? A: 1. Place ball 2. Wait for referee 3. Kick forward"""
        
        elif 'multiple choice' in question_type or question_type == 'multiple choice':
            return """FORMAT: ONLY the letter (A, B, C, or D). NOTHING ELSE.

Example: Q: Which won? A) France B) Brazil A: A"""
        
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
        
        # Generate using Ollama
        try:
            answer = self.llm.invoke(prompt)
            
            answer = self._post_process_answer(answer, question_type)
            
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
        import re
        
        answer = answer.strip()
        question_type = question_type.lower()
        
        prefixes = [
            "Answer:",
            "The answer is:",
            "The answer is",
            "Response:",
            "Here is the answer:",
            "Here's the answer:",
            "A:",
        ]
        
        for prefix in prefixes:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix):].strip()
                if answer and answer[0] in [':', '-']:
                    answer = answer[1:].strip()
        
        if 'multiple choice' in question_type:
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
            
            return 'A'
        
        elif question_type == 'list':
            answer = re.sub(r'^\s*[\d\.\-\•\*]+\s*', '', answer, flags=re.MULTILINE)
            answer = answer.replace('\n', '\t').replace(',', '\t')
            answer = re.sub(r'\t+', '\t', answer)
            answer = re.sub(r'\s+', ' ', answer)
            
            items = [item.strip() for item in answer.split('\t') if item.strip()]
            if items and items[-1].lower().startswith('and '):
                items[-1] = items[-1][4:]
            
            return '\t'.join(items)
        
        elif 'instruction' in question_type:
            lines = answer.split('\n')
            cleaned_lines = []
            step_num = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if not re.match(r'^\d+\.', line):
                    line = f"{step_num}. {line}"
                    step_num += 1
                else:
                    line = re.sub(r'^\d+\.', f'{step_num}.', line)
                    step_num += 1
                
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        elif question_type == 'factoid':
            words = answer.split()
            if len(words) > 10:
                answer = ' '.join(words[:10])
        
        return answer
