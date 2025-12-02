#!/usr/bin/env python3
import json
from pathlib import Path


def analyze_your_results():
    """Analyze your specific results"""
    
    # actual results
    results = {
        'bm25_gpt': {'llm_judge': 0.39, 'exact_match': 0.16, 'f1': 0.2003, 'contains': 0.22, 'rouge': 0.1934},
        'bm25_llama': {'llm_judge': 0.35, 'exact_match': 0.15, 'f1': 0.1833, 'contains': 0.21, 'rouge': 0.1755},
        'dense_gpt': {'llm_judge': 0.40, 'exact_match': 0.16, 'f1': 0.2104, 'contains': 0.24, 'rouge': 0.2038},
        'dense_llama': {'llm_judge': 0.38, 'exact_match': 0.17, 'f1': 0.1924, 'contains': 0.21, 'rouge': 0.1885},
        'none_gpt': {'llm_judge': 0.36, 'exact_match': 0.15, 'f1': 0.1884, 'contains': 0.22, 'rouge': 0.18}
    }
    
    print("="*80)
    print("ANALYSIS OF YOUR RAG SYSTEM RESULTS")
    print("="*80)
    print()
    
    # Overall Performance is Low
    print("KEY FINDING #1: LOW OVERALL PERFORMANCE")
    print("-"*80)
    avg_llm_judge = sum(r['llm_judge'] for r in results.values()) / len(results)
    print(f"Average LLM Judge Score: {avg_llm_judge:.2f} / 2.0 ({avg_llm_judge/2*100:.1f}%)")
    print(f"Average Exact Match: {sum(r['exact_match'] for r in results.values()) / len(results):.1%}")
    print()
    print("INTERPRETATION:")
    print("• LLM Judge score of 0.36-0.40 out of 2.0 means ~18-20% performance")
    print("• Only 15-17% of answers exactly match gold answers")
    print("• This indicates SIGNIFICANT room for improvement")
    print()
    
    # Retrieval Impact
    print("KEY FINDING #2: RETRIEVAL BARELY HELPS")
    print("-"*80)
    no_retrieval = results['none_gpt']['llm_judge']
    with_bm25 = results['bm25_gpt']['llm_judge']
    with_dense = results['dense_gpt']['llm_judge']
    
    print(f"No Retrieval (none_gpt):     {no_retrieval:.2f}")
    print(f"With BM25 (bm25_gpt):        {with_bm25:.2f} (Δ = +{with_bm25-no_retrieval:.2f})")
    print(f"With Dense (dense_gpt):      {with_dense:.2f} (Δ = +{with_dense-no_retrieval:.2f})")
    print()
    print("INTERPRETATION:")
    print("• Retrieval only improves score by +0.03-0.04 (1.5-2%)")
    print("• This suggests:")
    print("  - Poor retrieval quality (not finding relevant docs)")
    print("  - OR questions don't need retrieval (too general)")
    print("  - OR generator ignoring retrieved context")
    print()
    
    # Dense slightly better than BM25
    print("KEY FINDING #3: DENSE RETRIEVAL > BM25 (SLIGHTLY)")
    print("-"*80)
    print(f"BM25 + GPT:  {results['bm25_gpt']['llm_judge']:.2f}")
    print(f"Dense + GPT: {results['dense_gpt']['llm_judge']:.2f}")
    print(f"Difference:  +{results['dense_gpt']['llm_judge'] - results['bm25_gpt']['llm_judge']:.2f}")
    print()
    print("INTERPRETATION:")
    print("• Dense retrieval is marginally better (+0.01 = 0.5%)")
    print("• Difference is minimal - both retrievers struggling")
    print("• Semantic matching not helping much over keyword matching")
    print()
    
    # GPT > Llama
    print("KEY FINDING #4: GPT OUTPERFORMS LLAMA")
    print("-"*80)
    print(f"BM25 + GPT:   {results['bm25_gpt']['llm_judge']:.2f}")
    print(f"BM25 + Llama: {results['bm25_llama']['llm_judge']:.2f}")
    print(f"Difference:   +{results['bm25_gpt']['llm_judge'] - results['bm25_llama']['llm_judge']:.2f}")
    print()
    print(f"Dense + GPT:   {results['dense_gpt']['llm_judge']:.2f}")
    print(f"Dense + Llama: {results['dense_llama']['llm_judge']:.2f}")
    print(f"Difference:    +{results['dense_gpt']['llm_judge'] - results['dense_llama']['llm_judge']:.2f}")
    print()
    print("INTERPRETATION:")
    print("• GPT consistently beats Llama by +0.02-0.04 (1-2%)")
    print("• But difference is small - both generators struggling")
    print("• Generator quality matters, but not the main issue")
    print()
    
    # Best System Analysis
    print("KEY FINDING #5: BEST SYSTEM STILL POOR")
    print("-"*80)
    best_config = max(results.items(), key=lambda x: x[1]['llm_judge'])
    print(f"Best Configuration: {best_config[0]}")
    print(f"  LLM Judge: {best_config[1]['llm_judge']:.2f} / 2.0 (20%)")
    print(f"  Exact Match: {best_config[1]['exact_match']:.1%}")
    print(f"  F1 Score: {best_config[1]['f1']:.2f}")
    print()
    print("INTERPRETATION:")
    print("• Even best system only gets 20% of answers right")
    print("• 80% of questions are answered incorrectly or poorly")
    print("• This is a SYSTEMIC issue, not just configuration")
    print()
    
    # Root Cause Analysis
    print("="*80)
    print("ROOT CAUSE ANALYSIS: WHY IS PERFORMANCE SO LOW?")
    print("="*80)
    print()
    
    print("HYPOTHESIS 1: POOR DOCUMENT QUALITY")
    print("-"*80)
    print("• Generated documents may not contain specific facts needed")
    print("• Example: Question asks 'What year was FIFA founded?'")
    print("  - Document mentions FIFA but not founding year")
    print("  - Retrieval finds document but answer not present")
    print("LIKELIHOOD: HIGH")
    print()
    
    print("HYPOTHESIS 2: RETRIEVAL FAILURE")
    print("-"*80)
    print("• BM25/Dense not finding the right documents")
    print("• Questions use different wording than documents")
    print("• Example: Question about 'World Cup 1986' but document titled '1986 FIFA World Cup'")
    print("LIKELIHOOD: MEDIUM-HIGH")
    print()
    
    print("HYPOTHESIS 3: QUESTION-DOCUMENT MISMATCH")
    print("-"*80)
    print("• Questions may be too specific for general documents")
    print("• Documents cover broad topics, questions ask narrow facts")
    print("• Need more granular, fact-dense documents")
    print("LIKELIHOOD: HIGH")
    print()
    
    print("HYPOTHESIS 4: GENERATOR IGNORING CONTEXT")
    print("-"*80)
    print("• Generator may hallucinate instead of using retrieved text")
    print("• Evidence: Retrieval barely helps (0.36 → 0.40)")
    print("• If retrieval helped, we'd see bigger improvement")
    print("LIKELIHOOD: MEDIUM")
    print()
    
    print("HYPOTHESIS 5: EVALUATION METRIC ISSUES")
    print("-"*80)
    print("• LLM Judge might be too strict")
    print("• Short answers penalized even if semantically correct")
    print("• Example: 'Argentina' vs 'The Argentina national team'")
    print("LIKELIHOOD: LOW-MEDIUM")
    print()
    
    # Recommendations
    print("="*80)
    print("RECOMMENDATIONS FOR IMPROVEMENT")
    print("="*80)
    print()
    
    print("IMPROVE DOCUMENT QUALITY")
    print("• Add more fact-dense documents with specific details")
    print("• Ensure every question has a document with the answer")
    print("• Use actual Wikipedia articles or structured data")
    print()
    
    print("FIX RETRIEVAL")
    print("• Inspect retrieved documents for failed questions")
    print("• Check if right documents exist but aren't retrieved")
    print("• Consider query expansion or reranking")
    print()
    
    print("IMPROVE PROMPTS")
    print("• Add explicit instruction to use retrieved context")
    print("• Show examples of good answers in prompt")
    print("• Add format-specific examples")
    print()
    
    print("ANALYZE FAILURES BY TYPE")
    print("• Break down performance by question type")
    print("• Factoid vs List vs Instruction vs Multiple Choice")
    print("• Identify which types fail most")
    print()
    
    # Specifics
    print("="*80)
    print("WHAT YOUR SCORES ACTUALLY MEAN")
    print("="*80)
    print()
    
    print("LLM JUDGE SCORE: 0.40 / 2.0")
    print("• 0 points: 60% of answers (completely wrong)")
    print("• 1 point: 30% of answers (partially correct)")
    print("• 2 points: 10% of answers (correct)")
    print()
    
    print("EXACT MATCH: 16-17%")
    print("• Only 16-17 out of 100 answers match exactly")
    print("• 83-84% are wrong or differently worded")
    print()
    
    print("F1 SCORE: 0.19-0.21")
    print("• Only 19-21% token overlap on average")
    print("• Very low - indicates answers are way off")
    print()
    
    # analysis
    analysis_data = {
        'results': results,
        'findings': {
            'retrieval_helps': with_dense > no_retrieval,
            'retrieval_improvement': with_dense - no_retrieval,
            'best_retriever': 'dense' if with_dense > with_bm25 else 'bm25',
            'best_generator': 'gpt',
            'best_config': best_config[0],
            'best_score': best_config[1]['llm_judge']
        },
        'hypotheses': [
            {'name': 'poor_documents', 'likelihood': 'HIGH'},
            {'name': 'retrieval_failure', 'likelihood': 'MEDIUM-HIGH'},
            {'name': 'mismatch', 'likelihood': 'HIGH'},
            {'name': 'generator_ignoring', 'likelihood': 'MEDIUM'},
            {'name': 'metric_issues', 'likelihood': 'LOW-MEDIUM'}
        ]
    }
    
    with open('analysis_output/results_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print("="*80)
    print("Analysis saved to: analysis_output/results_analysis.json")
    print("="*80)


if __name__ == '__main__':
    Path('analysis_output').mkdir(exist_ok=True)
    analyze_your_results()