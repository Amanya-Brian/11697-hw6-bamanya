#!/bin/bash
# run_open_weight.sh - Run configurations using only open-weight models (no API costs)

set -e

echo "========================================="
echo "Running Open-Weight Configurations Only"
echo "========================================="
echo ""
echo "This script runs only BM25 + Llama (fully open-weight)"
echo "No API keys required!"
echo ""

# Configuration
QUESTIONS="data/question.tsv"
CORPUS="data/corpus"
TOP_K=3

# Create output directory
mkdir -p output/prediction

# BM25 + Llama (fully open-weight, no API calls)
echo "========================================="
echo "BM25 + Llama (Open-Weight)"
echo "========================================="
python src/rag_system.py \
  --retriever bm25 \
  --generator llama \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K

echo ""
echo "========================================="
echo "Complete!"
echo "========================================="
echo ""
echo "Output file:"
ls -lh output/prediction/bm25_llama.tsv