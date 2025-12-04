from typing import List, Set, Tuple
import re
from collections import Counter


class AutomaticMetricsEvaluator:
    
    def __init__(self):
        """Initialize automatic metrics evaluator"""
        pass
    
    def normalize_answer(self, text: str) -> str:
        """
        Normalize answer text for comparison
        
        Args:
            text: Answer text
            
        Returns:
            Normalized text
        """
        # to lowercase
        text = text.lower()
        
        # remove articles punctuation and whitespace
        text = re.sub(r'\b(a|an|the)\b', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return self.normalize_answer(text).split()
    
    def exact_match(self, gold_answers: List[str], predicted_answer: str) -> int:
        """
        Calculate exact match score
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            
        Returns:
            1 if exact match, 0 otherwise
        """
        if not predicted_answer or not predicted_answer.strip():
            return 0
        
        pred_norm = self.normalize_answer(predicted_answer)
        
        # if matches any gold answer
        for gold in gold_answers:
            gold_norm = self.normalize_answer(gold)
            if pred_norm == gold_norm:
                return 1
        
        return 0
    
    def f1_score(self, gold_answers: List[str], predicted_answer: str) -> float:
        """
        F1 score based on token overlap
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            
        Returns:
            F1 score (0.0 to 1.0)
        """
        if not predicted_answer or not predicted_answer.strip():
            return 0.0
        
        # predicted tokens
        pred_tokens = self.tokenize(predicted_answer)
        
        if not pred_tokens:
            return 0.0
        
        # max f1
        max_f1 = 0.0
        
        for gold in gold_answers:
            gold_tokens = self.tokenize(gold)
            
            if not gold_tokens:
                continue
            
            # token overlap
            pred_counter = Counter(pred_tokens)
            gold_counter = Counter(gold_tokens)
            
            # tokens in both
            tp = sum((pred_counter & gold_counter).values())
            
            # Precision and recall
            precision = tp / len(pred_tokens) if pred_tokens else 0.0
            recall = tp / len(gold_tokens) if gold_tokens else 0.0
            
            # F1 score
            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
                max_f1 = max(max_f1, f1)
        
        return max_f1
    
    def contains_match(self, gold_answers: List[str], predicted_answer: str) -> int:
        """
        Check if predicted answer contains any gold answer
        Useful for multiple choice where answer might include explanation
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            
        Returns:
            1 if contains match, 0 otherwise
        """
        if not predicted_answer or not predicted_answer.strip():
            return 0
        
        pred_norm = self.normalize_answer(predicted_answer)
        
        for gold in gold_answers:
            gold_norm = self.normalize_answer(gold)
            if gold_norm in pred_norm or pred_norm in gold_norm:
                return 1
        
        return 0
    
    def evaluate_single(
        self,
        gold_answers: List[str],
        predicted_answer: str,
        question_type: str = None
    ) -> dict:
        """
        Evaluate a single prediction with multiple metrics
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            question_type: Type of question (optional, for type-specific metrics)
            
        Returns:
            Dictionary of metric scores
        """
        results = {
            'exact_match': self.exact_match(gold_answers, predicted_answer),
            'f1_score': self.f1_score(gold_answers, predicted_answer),
            'contains_match': self.contains_match(gold_answers, predicted_answer)
        }
        
        return results


class ROUGEEvaluator:
    """ROUGE-L evaluator for list and instruction questions"""
    
    def __init__(self):
        """Initialize ROUGE evaluator"""
        try:
            from rouge_score import rouge_scorer
            self.scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            print("ROUGE evaluator initialized successfully")
        except ImportError:
            print("\n" + "="*60)
            print("WARNING: rouge-score not installed")
            print("Install with: pip install rouge-score")
            print("ROUGE-L scores will be 0.0")
            print("="*60 + "\n")
            self.scorer = None
        except Exception as e:
            print(f"\nWarning: Could not initialize ROUGE: {e}")
            print("ROUGE-L scores will be 0.0\n")
            self.scorer = None
    
    def _simple_rouge_l(self, reference: str, hypothesis: str) -> float:
        """
        Simple ROUGE-L implementation without external library
        Based on longest common subsequence
        
        Args:
            reference: Reference text
            hypothesis: Hypothesis text
            
        Returns:
            ROUGE-L F1 score
        """
        # Tokenize
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()
        
        if not ref_tokens or not hyp_tokens:
            return 0.0
        
        # Compute LCS length
        lcs_length = self._lcs_length(ref_tokens, hyp_tokens)
        
        if lcs_length == 0:
            return 0.0
        
        # Precision and recall
        precision = lcs_length / len(hyp_tokens)
        recall = lcs_length / len(ref_tokens)
        
        # F1 score
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def _lcs_length(self, seq1: list, seq2: list) -> int:
        """
        Compute length of longest common subsequence
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            Length of LCS
        """
        m, n = len(seq1), len(seq2)
        
        # DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def rouge_l(self, gold_answers: List[str], predicted_answer: str) -> float:
        """
        Calculate ROUGE-L score
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            
        Returns:
            ROUGE-L F1 score (0.0 to 1.0)
        """
        # Handle empty or None inputs
        if not predicted_answer or not predicted_answer.strip():
            return 0.0
        
        if not gold_answers or all(not g or not g.strip() for g in gold_answers):
            return 0.0
        
        # Use library version if available
        if self.scorer is not None:
            max_rouge = 0.0
            
            for gold in gold_answers:
                # Skip empty gold answers
                if not gold or not gold.strip():
                    continue
                
                try:
                    # Clean inputs - remove extra whitespace
                    gold_clean = ' '.join(gold.strip().split())
                    pred_clean = ' '.join(predicted_answer.strip().split())
                    
                    # Skip if either is now empty
                    if not gold_clean or not pred_clean:
                        continue
                    
                    scores = self.scorer.score(gold_clean, pred_clean)
                    rouge_l_f1 = scores['rougeL'].fmeasure
                    max_rouge = max(max_rouge, rouge_l_f1)
                    
                except Exception as e:
                    # If library fails, fallback to simple implementation
                    try:
                        rouge_score = self._simple_rouge_l(gold, predicted_answer)
                        max_rouge = max(max_rouge, rouge_score)
                    except:
                        pass  # Skip this gold answer
            
            return max_rouge
        
        # Use simple implementation if library not available
        else:
            max_rouge = 0.0
            
            for gold in gold_answers:
                if not gold or not gold.strip():
                    continue
                
                try:
                    rouge_score = self._simple_rouge_l(gold, predicted_answer)
                    max_rouge = max(max_rouge, rouge_score)
                except:
                    pass  # Skip this gold answer
            
            return max_rouge
    
    def evaluate_single(self, gold_answers: List[str], predicted_answer: str) -> dict:
        """
        Evaluate a single prediction
        
        Args:
            gold_answers: List of acceptable gold answers
            predicted_answer: Predicted answer
            
        Returns:
            Dictionary with ROUGE score
        """
        return {
            'rouge_l': self.rouge_l(gold_answers, predicted_answer)
        }