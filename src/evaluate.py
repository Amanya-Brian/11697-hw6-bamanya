#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Tuple
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_questions, load_answers
from evaluators.llm_judge import LLMJudgeEvaluator
from evaluators.automatic_metrics import AutomaticMetricsEvaluator, ROUGEEvaluator


def load_predictions(prediction_file: str) -> Tuple[List[str], List[Dict]]:
    """
    Load predictions from TSV file
    
    Args:
        prediction_file: Path to prediction TSV file
        
    Returns:
        Tuple of (predictions, metadata_list)
    """
    predictions = []
    metadata_list = []
    
    with open(prediction_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                predictions.append("")
                metadata_list.append({})
                continue
            
            parts = line.split('\t')
            
            prediction = parts[0] if len(parts) > 0 else ""
            predictions.append(prediction)
            
            if len(parts) > 1:
                try:
                    metadata = json.loads(parts[1])
                except:
                    metadata = {'raw': parts[1]}
            else:
                metadata = {}
            
            metadata_list.append(metadata)
    
    return predictions, metadata_list


def evaluate_predictions(
    questions: List[str],
    question_types: List[str],
    gold_answers: List[List[str]],
    predictions: List[str],
    use_llm_judge: bool = True,
    use_automatic: bool = True,
    use_rouge: bool = True
) -> List[Dict]:
    """
    Evaluate all predictions
    
    Args:
        questions: List of questions
        question_types: List of question types
        gold_answers: List of gold answer lists
        predictions: List of predicted answers
        use_llm_judge: Whether to use LLM as judge
        use_automatic: Whether to use automatic metrics
        use_rouge: Whether to use ROUGE
        
    Returns:
        List of evaluation result dictionaries
    """
    evaluators = {}
    
    if use_llm_judge:
        print("Initializing LLM Judge...")
        evaluators['llm_judge'] = LLMJudgeEvaluator()
    
    if use_automatic:
        evaluators['automatic'] = AutomaticMetricsEvaluator()
    
    if use_rouge:
        print("Initializing ROUGE evaluator...")
        evaluators['rouge'] = ROUGEEvaluator()
    
    results = []
    
    print(f"Evaluating {len(predictions)} predictions...")
    
    for i, (question, qtype, gold, pred) in enumerate(tqdm(
        zip(questions, question_types, gold_answers, predictions),
        total=len(predictions),
        desc="Evaluating"
    )):
        result = {
            'question_id': i,
            'question': question,
            'question_type': qtype,
            'gold_answers': gold,
            'prediction': pred
        }
        
        if 'llm_judge' in evaluators:
            try:
                score, reasoning = evaluators['llm_judge'].evaluate_single(
                    question=question,
                    question_type=qtype,
                    gold_answer=gold,
                    predicted_answer=pred
                )
                result['llm_judge_score'] = score
                result['llm_judge_reasoning'] = reasoning
            except Exception as e:
                print(f"\nError in LLM judge for question {i}: {e}")
                result['llm_judge_score'] = 0
                result['llm_judge_reasoning'] = f"Error: {str(e)}"
        
        if 'automatic' in evaluators:
            auto_scores = evaluators['automatic'].evaluate_single(gold, pred, qtype)
            result['exact_match'] = auto_scores['exact_match']
            result['f1_score'] = auto_scores['f1_score']
            result['contains_match'] = auto_scores['contains_match']
        
        if 'rouge' in evaluators:
            rouge_scores = evaluators['rouge'].evaluate_single(gold, pred)
            result['rouge_l'] = rouge_scores['rouge_l']
        
        results.append(result)
    
    # judge stats
    if 'llm_judge' in evaluators:
        stats = evaluators['llm_judge'].get_stats()
        print(f"\nLLM Judge Stats:")
        print(f"  Total API calls: {stats['total_calls']}")
        print(f"  Total tokens used: {stats['total_tokens']}")
    
    return results


def compute_aggregate_scores(results: List[Dict]) -> Dict:
    """
    Compute aggregate scores across all predictions
    
    Args:
        results: List of evaluation results
        
    Returns:
        Dictionary of aggregate scores
    """
    aggregates = {}
    
    # non-empty predictions
    non_empty = sum(1 for r in results if r['prediction'] and r['prediction'].strip())
    total = len(results)
    
    aggregates['total_questions'] = total
    aggregates['non_empty_predictions'] = non_empty
    aggregates['empty_predictions'] = total - non_empty
    
    # LLM Judge
    if 'llm_judge_score' in results[0]:
        scores = [r['llm_judge_score'] for r in results]
        aggregates['llm_judge_avg'] = sum(scores) / len(scores)
        aggregates['llm_judge_0'] = sum(1 for s in scores if s == 0)
        aggregates['llm_judge_1'] = sum(1 for s in scores if s == 1)
        aggregates['llm_judge_2'] = sum(1 for s in scores if s == 2)
    
    if 'exact_match' in results[0]:
        aggregates['exact_match_avg'] = sum(r['exact_match'] for r in results) / len(results)
    
    if 'f1_score' in results[0]:
        aggregates['f1_score_avg'] = sum(r['f1_score'] for r in results) / len(results)
    
    if 'contains_match' in results[0]:
        aggregates['contains_match_avg'] = sum(r['contains_match'] for r in results) / len(results)
    
    if 'rouge_l' in results[0]:
        aggregates['rouge_l_avg'] = sum(r['rouge_l'] for r in results) / len(results)
    
    return aggregates


def save_evaluation_results(
    results: List[Dict],
    output_file: str,
    format_type: str = 'tsv'
):
    """
    Save evaluation results to file
    
    Args:
        results: List of evaluation results
        output_file: Output file path
        format_type: 'tsv' or 'json'
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type == 'tsv':
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                scores = []
                
                if 'llm_judge_score' in result:
                    scores.append(str(result['llm_judge_score']))
                
                if 'exact_match' in result:
                    scores.append(str(result['exact_match']))
                
                if 'f1_score' in result:
                    scores.append(f"{result['f1_score']:.4f}")
                
                if 'contains_match' in result:
                    scores.append(str(result['contains_match']))
                
                if 'rouge_l' in result:
                    scores.append(f"{result['rouge_l']:.4f}")
                
                f.write('\t'.join(scores) + '\n')
    
    elif format_type == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)


def main():
    """Main evaluation entry point"""
    parser = argparse.ArgumentParser(
        description='Evaluate RAG system predictions'
    )
    parser.add_argument(
        '--prediction_file',
        type=str,
        required=True,
        help='Path to prediction TSV file'
    )
    parser.add_argument(
        '--questions',
        type=str,
        default='data/question.tsv',
        help='Path to questions TSV file'
    )
    parser.add_argument(
        '--answers',
        type=str,
        default='data/answer.tsv',
        help='Path to answers TSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output evaluation file (default: output/evaluation/<name>.tsv)'
    )
    parser.add_argument(
        '--detailed_output',
        type=str,
        default=None,
        help='Detailed JSON output file (optional)'
    )
    parser.add_argument(
        '--no_llm_judge',
        action='store_true',
        help='Skip LLM judge (saves API costs)'
    )
    parser.add_argument(
        '--metrics',
        type=str,
        nargs='+',
        default=['llm_judge', 'f1', 'exact_match', 'rouge'],
        help='Metrics to use (default: all)'
    )
    
    args = parser.parse_args()
    
    if args.output is None:
        pred_name = Path(args.prediction_file).stem
        output_dir = Path('output/evaluation')
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = output_dir / f"{pred_name}.tsv"
    
    # Load data
    print("="*80)
    print("Loading data...")
    print(f"  Questions: {args.questions}")
    print(f"  Answers: {args.answers}")
    print(f"  Predictions: {args.prediction_file}")
    print("="*80)
    
    questions, question_types = load_questions(args.questions)
    gold_answers = load_answers(args.answers)
    predictions, metadata = load_predictions(args.prediction_file)
    
    print(f"\nLoaded:")
    print(f"  {len(questions)} questions")
    print(f"  {len(predictions)} predictions")
    
    # lengths match
    if len(questions) != len(predictions):
        print(f"\nWarning: Number of questions ({len(questions)}) != predictions ({len(predictions)})")
        min_len = min(len(questions), len(predictions), len(gold_answers))
        questions = questions[:min_len]
        question_types = question_types[:min_len]
        gold_answers = gold_answers[:min_len]
        predictions = predictions[:min_len]
        print(f"Using first {min_len} items")
    
    # which metrics to use
    use_llm_judge = 'llm_judge' in args.metrics and not args.no_llm_judge
    use_automatic = any(m in args.metrics for m in ['f1', 'exact_match', 'contains'])
    use_rouge = 'rouge' in args.metrics
    
    print(f"\nMetrics to use:")
    if use_llm_judge:
        print("  ✓ LLM-as-a-Judge")
    if use_automatic:
        print("  ✓ Automatic (EM, F1, Contains)")
    if use_rouge:
        print("  ✓ ROUGE-L")
    print()
    
    # Evaluate
    results = evaluate_predictions(
        questions=questions,
        question_types=question_types,
        gold_answers=gold_answers,
        predictions=predictions,
        use_llm_judge=use_llm_judge,
        use_automatic=use_automatic,
        use_rouge=use_rouge
    )
    
    # aggregates
    print("\n" + "="*80)
    print("Aggregate Scores:")
    print("="*80)
    
    aggregates = compute_aggregate_scores(results)
    
    for key, value in aggregates.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # results
    print(f"\nSaving evaluation results...")
    print(f"  TSV output: {args.output}")
    save_evaluation_results(results, args.output, format_type='tsv')
    
    if args.detailed_output:
        print(f"  JSON output: {args.detailed_output}")
        save_evaluation_results(results, args.detailed_output, format_type='json')
    
    print("\n" + "="*80)
    print("Evaluation complete!")
    print("="*80)


if __name__ == '__main__':
    main()