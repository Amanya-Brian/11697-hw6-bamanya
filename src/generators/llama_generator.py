"""
Llama Generator - Open-weight generator using Llama models
Uses Hugging Face transformers library
"""

from typing import Tuple, Dict
import torch


class LlamaGenerator:
    """Generator using open-weight Llama models"""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        device: str = None
    ):
        """
        Initialize Llama generator
        
        Args:
            model_name: Hugging Face model name
            device: Device to run model on ('cuda' or 'cpu')
        """
        self.model_name = model_name
        
        # device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"Loading Llama model on {self.device}...")
        
        # model and tokenizer
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map='auto' if self.device == 'cuda' else None
            )
            
            if self.device == 'cpu':
                self.model = self.model.to(self.device)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print(f"Model loaded successfully on {self.device}")
            
        except ImportError:
            raise ImportError(
                "Transformers library not installed. "
                "Install with: pip install transformers torch"
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to smaller model...")
            
            try:
                self.model_name = "meta-llama/Llama-3.2-1B-Instruct"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                    device_map='auto' if self.device == 'cuda' else None
                )
                if self.device == 'cpu':
                    self.model = self.model.to(self.device)
                print(f"Loaded fallback model: {self.model_name}")
            except:
                raise RuntimeError("Could not load Llama model")
    
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

Context:
{context}

Question: {question}

{format_instructions}

Answer:"""
        else:
            prompt = f"""You are a knowledgeable football expert. Answer the question.

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
            return "Give a brief, direct answer (a few words or short phrase only)."
        
        elif question_type == 'list':
            return "List your answer with numbered items."
        
        elif question_type == 'instruction' or 'instruction' in question_type:
            return "Provide numbered step-by-step instructions."
        
        elif 'multiple choice' in question_type or question_type == 'multiple choice':
            return "Answer with only the letter (A, B, C, or D)."
        
        else:
            return "Provide a clear answer."
    
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
        
        # tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.device)
        
        # generate
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.3,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # decode
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            answer = full_output[len(prompt):].strip()
            
            answer = self._post_process_answer(answer, question_type)
            
            metadata = {
                'model': self.model_name,
                'device': self.device,
                'tokens_generated': len(outputs[0]) - len(inputs['input_ids'][0])
            }
            
            return answer, metadata
        
        except Exception as e:
            print(f"Error generating answer: {e}")
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
        prefixes = [
            "Answer:",
            "The answer is:",
            "Response:",
        ]
        
        for prefix in prefixes:
            if answer.lower().startswith(prefix.lower()):
                answer = answer[len(prefix):].strip()
        
        if 'multiple choice' in question_type.lower():
            import re
            match = re.search(r'\b([A-D])\b', answer)
            if match:
                answer = match.group(1)
        
        if question_type.lower() == 'factoid':
            sentences = answer.split('.')
            if sentences:
                answer = sentences[0].strip()
            words = answer.split()
            if len(words) > 50:
                answer = ' '.join(words[:50])
        
        return answer.strip()