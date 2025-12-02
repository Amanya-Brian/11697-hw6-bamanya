#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import re

sys.path.insert(0, 'src')
from utils.data_loader import load_questions, load_answers


def analyze_prediction_errors(
    questions: List[str],
    question_types: List[str],
    gold_answers: List[List[str]],
    predictions: List[str],
    eval_results: List[Dict]
) -> Dict:
    """Comprehensive error analysis"""
    
    analysis = {
        'overall': {},
        'by_question_type': {},
        'failure_patterns': [],
        'retrieval_issues': [],
        'generation_issues': [],
        'format_issues': []
    }
    
    # Overall statistics
    total = len(questions)
    perfect_scores = sum(1 for r in eval_results if r.get('llm_judge_score', 0) == 2)
    partial_scores = sum(1 for r in eval_results if r.get('llm_judge_score', 0) == 1)
    zero_scores = sum(1 for r in eval_results if r.get('llm_judge_score', 0) == 0)
    
    analysis['overall'] = {
        'total_questions': total,
        'perfect_answers': perfect_scores,
        'partial_answers': partial_scores,
        'failed_answers': zero_scores,
        'perfect_rate': perfect_scores / total,
        'failure_rate': zero_scores / total
    }
    
    # Analyze by question type
    by_type = defaultdict(lambda: {'total': 0, 'perfect': 0, 'partial': 0, 'failed': 0})
    
    for i, (qtype, result) in enumerate(zip(question_types, eval_results)):
        score = result.get('llm_judge_score', 0)
        by_type[qtype]['total'] += 1
        if score == 2:
            by_type[qtype]['perfect'] += 1
        elif score == 1:
            by_type[qtype]['partial'] += 1
        else:
            by_type[qtype]['failed'] += 1
    
    for qtype, stats in by_type.items():
        stats['success_rate'] = stats['perfect'] / stats['total'] if stats['total'] > 0 else 0
        stats['failure_rate'] = stats['failed'] / stats['total'] if stats['total'] > 0 else 0
    
    analysis['by_question_type'] = dict(by_type)
    
    # Identify failure patterns
    for i, result in enumerate(eval_results):
        if result.get('llm_judge_score', 0) == 0:
            pattern = analyze_failure_pattern(
                question=questions[i],
                question_type=question_types[i],
                gold_answer=gold_answers[i],
                prediction=predictions[i],
                result=result
            )
            analysis['failure_patterns'].append(pattern)
    
    return analysis


def analyze_failure_pattern(
    question: str,
    question_type: str,
    gold_answer: List[str],
    prediction: str,
    result: Dict
) -> Dict:
    """Analyze why a specific prediction failed"""
    
    pattern = {
        'question': question[:100] + '...' if len(question) > 100 else question,
        'type': question_type,
        'gold': gold_answer[0] if gold_answer else '',
        'prediction': prediction[:100] + '...' if len(prediction) > 100 else prediction,
        'issues': []
    }
    
    # Empty prediction
    if not prediction or not prediction.strip():
        pattern['issues'].append('EMPTY_PREDICTION')
        pattern['category'] = 'generation_failure'
        return pattern
    
    # Format mismatch
    if question_type == 'multiple choice':
        if not re.match(r'^[A-D]$', prediction.strip()):
            pattern['issues'].append('WRONG_FORMAT_MC')
            pattern['category'] = 'format_error'
    
    if question_type == 'factoid':
        if len(prediction.split()) > 20:
            pattern['issues'].append('TOO_VERBOSE_FACTOID')
            pattern['category'] = 'format_error'
    
    # Hallucination detection
    pred_lower = prediction.lower()
    gold_lower = ' '.join(gold_answer).lower()
    
    if 'i don\'t know' in pred_lower or 'cannot answer' in pred_lower:
        pattern['issues'].append('EXPLICIT_REFUSAL')
        pattern['category'] = 'retrieval_failure'
    
    # Check if prediction is completely off-topic
    pred_tokens = set(pred_lower.split())
    gold_tokens = set(gold_lower.split())
    
    overlap = len(pred_tokens & gold_tokens)
    if overlap == 0 and len(pred_tokens) > 0:
        pattern['issues'].append('ZERO_OVERLAP')
        pattern['category'] = 'hallucination'
    
    # Retrieval context issues (if metadata available)
    if 'retrieved_doc_ids' in result:
        if not result['retrieved_doc_ids']:
            pattern['issues'].append('NO_RETRIEVAL')
            pattern['category'] = 'retrieval_failure'
    
    if not pattern['issues']:
        pattern['issues'].append('SEMANTIC_MISMATCH')
        pattern['category'] = 'generation_quality'
    
    return pattern


def analyze_retrieval_quality(predictions_file: str, questions: List[str]) -> Dict:
    """Analyze retrieval quality from metadata"""
    
    # Load predictions with metadata
    with open(predictions_file, 'r') as f:
        lines = f.readlines()
    
    retrieval_stats = {
        'total_retrievals': 0,
        'empty_retrievals': 0,
        'avg_score': 0.0,
        'low_score_retrievals': 0,
        'score_distribution': []
    }
    
    scores = []
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            try:
                metadata = json.loads(parts[1])
                if 'retrieval_scores' in metadata and metadata['retrieval_scores']:
                    max_score = max(metadata['retrieval_scores'])
                    scores.append(max_score)
                    
                    if max_score < 0.1:
                        retrieval_stats['low_score_retrievals'] += 1
                else:
                    retrieval_stats['empty_retrievals'] += 1
            except:
                pass
    
    retrieval_stats['total_retrievals'] = len(scores)
    if scores:
        retrieval_stats['avg_score'] = sum(scores) / len(scores)
        retrieval_stats['min_score'] = min(scores)
        retrieval_stats['max_score'] = max(scores)
    
    return retrieval_stats


def generate_failure_report(analysis: Dict, output_file: str):
    """Generate comprehensive failure analysis report"""
    
    report = []
    report.append("="*80)
    report.append("RAG SYSTEM FAILURE ANALYSIS")
    report.append("="*80)
    report.append("")
    
    # Overall stats
    report.append("OVERALL PERFORMANCE")
    report.append("-"*80)
    overall = analysis['overall']
    report.append(f"Total Questions: {overall['total_questions']}")
    report.append(f"Perfect Answers: {overall['perfect_answers']} ({overall['perfect_rate']:.1%})")
    report.append(f"Partial Answers: {overall['partial_answers']}")
    report.append(f"Failed Answers: {overall['failed_answers']} ({overall['failure_rate']:.1%})")
    report.append("")
    
    # By question type
    report.append("PERFORMANCE BY QUESTION TYPE")
    report.append("-"*80)
    for qtype, stats in analysis['by_question_type'].items():
        report.append(f"\n{qtype.upper()}:")
        report.append(f"  Total: {stats['total']}")
        report.append(f"  Success Rate: {stats['success_rate']:.1%}")
        report.append(f"  Failure Rate: {stats['failure_rate']:.1%}")
        report.append(f"  Perfect: {stats['perfect']}, Partial: {stats['partial']}, Failed: {stats['failed']}")
    report.append("")
    
    # Failure patterns
    report.append("FAILURE PATTERN ANALYSIS")
    report.append("-"*80)
    
    # Count failure categories
    categories = Counter([p['category'] for p in analysis['failure_patterns']])
    issues = Counter([issue for p in analysis['failure_patterns'] for issue in p['issues']])
    
    report.append("\nFailure Categories:")
    for category, count in categories.most_common():
        pct = count / len(analysis['failure_patterns']) * 100 if analysis['failure_patterns'] else 0
        report.append(f"  {category}: {count} ({pct:.1f}%)")
    
    report.append("\nCommon Issues:")
    for issue, count in issues.most_common(10):
        pct = count / len(analysis['failure_patterns']) * 100 if analysis['failure_patterns'] else 0
        report.append(f"  {issue}: {count} ({pct:.1f}%)")
    
    # Sample failures
    report.append("\n" + "="*80)
    report.append("SAMPLE FAILURES (First 10)")
    report.append("="*80)
    
    for i, pattern in enumerate(analysis['failure_patterns'][:10], 1):
        report.append(f"\nFailure #{i} [{pattern['type']}] - {pattern['category']}")
        report.append(f"Q: {pattern['question']}")
        report.append(f"Gold: {pattern['gold']}")
        report.append(f"Pred: {pattern['prediction']}")
        report.append(f"Issues: {', '.join(pattern['issues'])}")
    
    # Write report
    report_text = '\n'.join(report)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    return report_text


def compare_configurations(eval_dir: str) -> Dict:
    """Compare why different configurations perform differently"""
    
    comparison = {
        'retriever_impact': {},
        'generator_impact': {},
        'combined_impact': {}
    }
    
    # Load all evaluation results
    configs = {}
    for eval_file in Path(eval_dir).glob('*.tsv'):
        config_name = eval_file.stem
        
        scores = []
        with open(eval_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if parts and parts[0]:
                    try:
                        llm_score = float(parts[0])
                        scores.append(llm_score)
                    except:
                        pass
        
        if scores:
            configs[config_name] = {
                'avg_score': sum(scores) / len(scores),
                'scores': scores
            }
    
    # Compare retrievers (BM25 vs Dense)
    if 'bm25_gpt' in configs and 'dense_gpt' in configs:
        comparison['retriever_impact']['bm25_vs_dense_with_gpt'] = {
            'bm25': configs['bm25_gpt']['avg_score'],
            'dense': configs['dense_gpt']['avg_score'],
            'difference': configs['dense_gpt']['avg_score'] - configs['bm25_gpt']['avg_score'],
            'winner': 'dense' if configs['dense_gpt']['avg_score'] > configs['bm25_gpt']['avg_score'] else 'bm25'
        }
    
    # Compare generators (GPT vs Llama)
    if 'bm25_gpt' in configs and 'bm25_llama' in configs:
        comparison['generator_impact']['gpt_vs_llama_with_bm25'] = {
            'gpt': configs['bm25_gpt']['avg_score'],
            'llama': configs['bm25_llama']['avg_score'],
            'difference': configs['bm25_gpt']['avg_score'] - configs['bm25_llama']['avg_score'],
            'winner': 'gpt' if configs['bm25_gpt']['avg_score'] > configs['bm25_llama']['avg_score'] else 'llama'
        }
    
    # Check if retrieval helps
    if 'none_gpt' in configs and 'bm25_gpt' in configs:
        comparison['retrieval_helps'] = {
            'no_retrieval': configs['none_gpt']['avg_score'],
            'with_retrieval': configs['bm25_gpt']['avg_score'],
            'improvement': configs['bm25_gpt']['avg_score'] - configs['none_gpt']['avg_score'],
            'helps': configs['bm25_gpt']['avg_score'] > configs['none_gpt']['avg_score']
        }
    
    return comparison


def main():
    parser = argparse.ArgumentParser(description='Advanced RAG Analysis')
    parser.add_argument('--prediction_file', type=str, required=True)
    parser.add_argument('--questions', type=str, default='data/question.tsv')
    parser.add_argument('--answers', type=str, default='data/answer.tsv')
    parser.add_argument('--eval_results', type=str, required=True, help='Detailed JSON eval results')
    parser.add_argument('--output_dir', type=str, default='analysis_output')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("ADVANCED RAG FAILURE ANALYSIS")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    questions, question_types = load_questions(args.questions)
    gold_answers = load_answers(args.answers)
    
    with open(args.prediction_file, 'r') as f:
        predictions = [line.split('\t')[0] for line in f]
    
    with open(args.eval_results, 'r') as f:
        eval_results = json.load(f)
    
    # Run analysis
    print("Analyzing failures...")
    analysis = analyze_prediction_errors(
        questions, question_types, gold_answers, predictions, eval_results
    )
    
    # Generate report
    report_file = f"{args.output_dir}/failure_analysis.txt"
    print(f"\nGenerating failure report: {report_file}")
    report = generate_failure_report(analysis, report_file)
    
    # Save detailed JSON
    json_file = f"{args.output_dir}/failure_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Print summary
    print("\n" + report[:1000])
    print(f"\nFull report saved to: {report_file}")
    print(f"Detailed JSON saved to: {json_file}")


if __name__ == '__main__':
    main()