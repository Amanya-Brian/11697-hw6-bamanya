import os
from typing import Tuple, Dict, List
import time


class LLMJudgeEvaluator:
    """Evaluator using LLM as a judge"""
    
    def __init__(self, model: str = "gpt-4o-mini-2024-07-18"):
        """
        Initialize LLM judge evaluator
        
        Args:
            model: OpenAI model to use as judge
        """
        self.model = model
        
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
        
        # Track costs
        self.total_tokens = 0
        self.total_calls = 0
    
    def _build_judge_prompt(
        self,
        question: str,
        question_type: str,
        gold_answer: List[str],
        predicted_answer: str
    ) -> str:
        """
        Build prompt for the LLM judge
        
        Args:
            question: The question
            question_type: Type of question
            gold_answer: Ground truth answer(s)
            predicted_answer: System's predicted answer
            
        Returns:
            Judge prompt
        """
        # Format gold answers based on question type
        if question_type == 'list':
            # For list questions, show all items (not as alternatives)
            gold_str = ", ".join(gold_answer)
            gold_str += " (all items required)"
        elif len(gold_answer) == 1:
            gold_str = gold_answer[0]
        else:
            # For other types, multiple gold answers are alternatives
            gold_str = " OR ".join([f'"{ans}"' for ans in gold_answer])
        
        prompt = f"""# Instruction
You are an expert evaluator for a football question answering system.
You will be given a question, the gold (correct) answer(s), and a system's predicted answer.

Your task is to provide a rating from 0 to 2:
- 0: The predicted answer is incorrect or does not match the gold answer
- 1: The predicted answer is partially correct or somewhat matches the gold answer
- 2: The predicted answer is correct and matches the gold answer

# Guidelines for Evaluation

**For FACTOID questions:**
- Check if the predicted answer contains the key information from gold answer
- Minor variations in wording are acceptable (e.g., "Messi" vs "Lionel Messi")
- The answer should be concise and direct

**For LIST questions:**
- The predicted answer should include ALL items from the gold answer
- Items can be in any order unless specified
- Partial credit (score 1) if at least 50% of items are present
- Score 0 if less than 50% of items are present
- Format doesn't matter (tabs, commas, newlines all acceptable)

**For INSTRUCTION questions:**
- Check if the main steps are covered
- Minor variations in wording or order are acceptable
- Partial credit if some key steps are included

**For MULTIPLE CHOICE questions:**
- Must match exactly the correct letter (A, B, C, or D)
- No partial credit for multiple choice

# Task
Now evaluate the following:

**Question Type:** {question_type}

**Question:** {question}

**Gold Answer:** {gold_str}

**Predicted Answer:** {predicted_answer}

Provide your evaluation in the following format:

Reasoning: (briefly explain your evaluation)
Score: (your rating as 0, 1, or 2)
"""
        
        return prompt
    
    def evaluate_single(
        self,
        question: str,
        question_type: str,
        gold_answer: List[str],
        predicted_answer: str
    ) -> Tuple[int, str]:
        """
        Evaluate a single prediction
        
        Args:
            question: The question
            question_type: Type of question
            gold_answer: Ground truth answer(s)
            predicted_answer: Predicted answer
            
        Returns:
            Tuple of (score, reasoning)
        """
        if not predicted_answer or predicted_answer.strip() == "":
            return 0, "Empty prediction"
        
        prompt = self._build_judge_prompt(question, question_type, gold_answer, predicted_answer)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator for question answering systems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for evaluation
                max_tokens=300
            )
            
            output = response.choices[0].message.content.strip()
            
            # Track usage
            self.total_tokens += response.usage.total_tokens
            self.total_calls += 1
            
            # Parse score from output
            score = self._parse_score(output)
            
            # Extract reasoning
            reasoning = self._extract_reasoning(output)
            
            return score, reasoning
            
        except Exception as e:
            print(f"Error in LLM judge: {e}")
            return 0, f"Error: {str(e)}"
    
    def _parse_score(self, output: str) -> int:
        """
        Parse score from LLM output
        
        Args:
            output: LLM response text
            
        Returns:
            Score (0, 1, or 2)
        """
        # Look for "Score: X" pattern
        import re
        
        # Try different patterns
        patterns = [
            r'Score:\s*(\d)',
            r'Rating:\s*(\d)',
            r'Final Score:\s*(\d)',
            r'\*\*Score:\*\*\s*(\d)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                # Clamp to valid range
                return max(0, min(2, score))
        
        # If no pattern found, try to find any digit 0-2 after "score"
        score_section = output.lower().split('score')[-1]
        for char in score_section:
            if char in ['0', '1', '2']:
                return int(char)
        
        # Default to 0 if can't parse
        print(f"Warning: Could not parse score from: {output[:100]}")
        return 0
    
    def _extract_reasoning(self, output: str) -> str:
        """
        Extract reasoning from LLM output
        
        Args:
            output: LLM response text
            
        Returns:
            Reasoning text
        """
        # Try to extract reasoning section
        import re
        
        match = re.search(r'Reasoning:\s*(.+?)(?=Score:|Rating:|$)', output, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If can't find, return first line
        return output.split('\n')[0][:200]
    
    def get_stats(self) -> Dict:
        """Get evaluation statistics"""
        return {
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'model': self.model
        }
