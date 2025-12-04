import argparse
from pathlib import Path
import json
from typing import Dict, List
import sys


def load_tsv_scores(tsv_file: str) -> List[List[float]]:
    """Load scores from TSV file"""
    scores = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            row_scores = []
            for val in parts:
                try:
                    row_scores.append(float(val))
                except:
                    row_scores.append(0.0)
            scores.append(row_scores)
    return scores


def compute_averages(scores: List[List[float]]) -> List[float]:
    """Compute average for each metric column"""
    if not scores:
        return []
    
    num_metrics = len(scores[0])
    averages = []
    
    for col in range(num_metrics):
        col_scores = [row[col] for row in scores if len(row) > col]
        avg = sum(col_scores) / len(col_scores) if col_scores else 0.0
        averages.append(avg)
    
    return averages


def generate_summary_report(eval_dir: str, output_file: str):
    """Generate summary report from all evaluation files"""
    
    eval_path = Path(eval_dir)
    
    # evaluation TSV files
    eval_files = list(eval_path.glob("*.tsv"))
    
    if not eval_files:
        print(f"No evaluation files found in {eval_dir}")
        sys.exit(1)
    
    print(f"Found {len(eval_files)} evaluation files")
    
    # results
    results = {}
    
    for eval_file in eval_files:
        config_name = eval_file.stem
        scores = load_tsv_scores(eval_file)
        averages = compute_averages(scores)
        
        results[config_name] = {
            'num_questions': len(scores),
            'averages': averages
        }
    
    # report
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("RAG SYSTEM EVALUATION SUMMARY")
    report_lines.append("="*80)
    report_lines.append("")
    
    metric_names = ['LLM Judge (0-2)', 'Exact Match', 'F1 Score', 'Contains Match', 'ROUGE-L']
    
    report_lines.append(f"Total configurations evaluated: {len(results)}")
    report_lines.append("")
    
    sorted_configs = sorted(results.items())
    
    report_lines.append("-"*80)
    report_lines.append("OVERALL SCORES BY CONFIGURATION")
    report_lines.append("-"*80)
    report_lines.append("")
    
    header = f"{'Configuration':<25}"
    for i, metric in enumerate(metric_names):
        if i < len(sorted_configs[0][1]['averages']):
            header += f"{metric:>12}"
    report_lines.append(header)
    report_lines.append("-"*80)
    
    for config_name, data in sorted_configs:
        row = f"{config_name:<25}"
        for score in data['averages']:
            row += f"{score:>12.4f}"
        report_lines.append(row)
    
    report_lines.append("")
    report_lines.append("")
    
    report_lines.append("-"*80)
    report_lines.append("DETAILED RESULTS")
    report_lines.append("-"*80)
    report_lines.append("")
    
    for config_name, data in sorted_configs:
        report_lines.append(f"Configuration: {config_name}")
        report_lines.append(f"  Questions evaluated: {data['num_questions']}")
        
        for i, avg in enumerate(data['averages']):
            if i < len(metric_names):
                metric = metric_names[i]
                report_lines.append(f"  {metric}: {avg:.4f}")
        
        report_lines.append("")
    
    report_lines.append("-"*80)
    report_lines.append("BEST CONFIGURATION PER METRIC")
    report_lines.append("-"*80)
    report_lines.append("")
    
    if sorted_configs:
        num_metrics = len(sorted_configs[0][1]['averages'])
        
        for metric_idx in range(num_metrics):
            if metric_idx < len(metric_names):
                metric_name = metric_names[metric_idx]
                
                best_config = None
                best_score = -1
                
                for config_name, data in sorted_configs:
                    if metric_idx < len(data['averages']):
                        score = data['averages'][metric_idx]
                        if score > best_score:
                            best_score = score
                            best_config = config_name
                
                if best_config:
                    report_lines.append(f"{metric_name}: {best_config} ({best_score:.4f})")
    
    report_lines.append("")
    report_lines.append("="*80)
    
    # report
    report_text = '\n'.join(report_lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(report_text)


def main():
    parser = argparse.ArgumentParser(
        description='Generate evaluation summary report'
    )
    parser.add_argument(
        '--eval_dir',
        type=str,
        default='output/evaluation',
        help='Directory containing evaluation TSV files'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='evaluation_summary.txt',
        help='Output file for summary report'
    )
    
    args = parser.parse_args()
    
    generate_summary_report(args.eval_dir, args.output)
    
    print(f"\nSummary report saved to: {args.output}")


if __name__ == '__main__':
    main()
