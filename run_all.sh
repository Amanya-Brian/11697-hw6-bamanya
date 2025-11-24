#!/bin/bash
# run_all.sh - Run all RAG system configurations

set -e  # Exit on error

echo "========================================="
echo "Running all RAG configurations"
echo "========================================="
echo ""

# Configuration
QUESTIONS="data/question.tsv"
CORPUS="data/corpus"
TOP_K=3

# Create output directory if it doesn't exist
mkdir -p output/prediction

echo "Configuration:"
echo "  Questions: $QUESTIONS"
echo "  Corpus: $CORPUS"
echo "  Top-K: $TOP_K"
echo ""

# 1. No Retrieval + GPT (Baseline)
echo "========================================="
echo "1/5: No Retrieval + GPT (Baseline)"
echo "========================================="
python src/rag_system.py \
  --retriever none \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS
echo ""

# 2. BM25 + GPT
echo "========================================="
echo "2/5: BM25 + GPT"
echo "========================================="
python src/rag_system.py \
  --retriever bm25 \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K
echo ""

# 3. BM25 + Llama
echo "========================================="
echo "3/5: BM25 + Llama"
echo "========================================="
python src/rag_system.py \
  --retriever bm25 \
  --generator llama \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K
echo ""

# 4. Dense + GPT
echo "========================================="
echo "4/5: Dense + GPT"
echo "========================================="
python src/rag_system.py \
  --retriever dense \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K
echo ""

# 5. Dense + Llama
echo "========================================="
echo "5/5: Dense + Llama"
echo "========================================="
python src/rag_system.py \
  --retriever dense \
  --generator llama \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K
echo ""

echo "========================================="
echo "All configurations complete!"
echo "========================================="
echo ""
echo "Output files in output/prediction/:"
ls -lh output/prediction/