# Football RAG System - HW6

A comprehensive Retrieval-Augmented Generation (RAG) system for answering football-related questions.

## Overview

This system implements:
- **1 No-Retrieval System**: Direct generation without retrieval
- **4 RAG Systems** (2x2 combinations):
  - **Retrievers**: BM25 (sparse/open-weight) + Dense (API-based embeddings)
  - **Generators**: GPT-4 (API-based) + Llama (open-weight)

## Project Structure

```
.
├── src/
│   ├── rag_system.py          # Main entry point
│   ├── retrievers/
│   │   ├── bm25_retriever.py  # Sparse retrieval (open-weight)
│   │   └── dense_retriever.py # Dense retrieval (API-based)
│   ├── generators/
│   │   ├── gpt_generator.py   # GPT-4 generator (API-based)
│   │   └── llama_generator.py # Llama generator (open-weight)
│   └── utils/
│       └── data_loader.py     # Data loading utilities
├── data/
│   ├── question.tsv           # Questions with types
│   ├── answer.tsv             # Ground truth answers
│   ├── evidence.tsv           # Evidence mapping
│   └── corpus/                # Document corpus
├── output/
│   └── prediction/            # Generated predictions
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# For API-based models (GPT and Dense retriever)
export OPENAI_API_KEY="your-api-key-here"

# Optional: For Hugging Face models (if using gated models)
export HUGGING_FACE_TOKEN="your-hf-token-here"
```

### 3. Prepare Data

Ensure your data directory contains:
- `question.tsv`: Questions in format `<question>\t<type>`
- `answer.tsv`: Ground truth answers (tab-separated for multiple answers)
- `evidence.tsv`: Evidence mapping in format `<url>\t<filename>`
- `corpus/`: Directory with all document files (.txt, .md, .pdf)

## Usage

### Command Line Interface

The main script accepts the following arguments:

```bash
python src/rag_system.py \
  --retriever <bm25|dense|none> \
  --generator <gpt|llama> \
  --questions <path-to-questions> \
  --corpus <path-to-corpus> \
  --output <output-file> \
  --top_k <number-of-docs>
```

### Running All 5 Required Configurations

#### 1. No Retrieval + GPT (Baseline)
```bash
python src/rag_system.py \
  --retriever none \
  --generator gpt \
  --questions data/question.tsv \
  --corpus data/corpus \
  --output output/prediction/none_gpt.tsv
```

#### 2. BM25 + GPT
```bash
python src/rag_system.py \
  --retriever bm25 \
  --generator gpt \
  --questions data/question.tsv \
  --corpus data/corpus \
  --output output/prediction/bm25_gpt.tsv \
  --top_k 3
```

#### 3. BM25 + Llama
```bash
python src/rag_system.py \
  --retriever bm25 \
  --generator llama \
  --questions data/question.tsv \
  --corpus data/corpus \
  --output output/prediction/bm25_llama.tsv \
  --top_k 3
```

#### 4. Dense + GPT
```bash
python src/rag_system.py \
  --retriever dense \
  --generator gpt \
  --questions data/question.tsv \
  --corpus data/corpus \
  --output output/prediction/dense_gpt.tsv \
  --top_k 3
```

#### 5. Dense + Llama
```bash
python src/rag_system.py \
  --retriever dense \
  --generator llama \
  --questions data/question.tsv \
  --corpus data/corpus \
  --output output/prediction/dense_llama.tsv \
  --top_k 3
```

### Batch Script

Create a bash script to run all configurations:

```bash
#!/bin/bash
# run_all.sh

echo "Running all RAG configurations..."

# Configuration
QUESTIONS="data/question.tsv"
CORPUS="data/corpus"
TOP_K=3

# 1. No Retrieval + GPT
echo "1/5: No Retrieval + GPT"
python src/rag_system.py \
  --retriever none \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS

# 2. BM25 + GPT
echo "2/5: BM25 + GPT"
python src/rag_system.py \
  --retriever bm25 \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K

# 3. BM25 + Llama
echo "3/5: BM25 + Llama"
python src/rag_system.py \
  --retriever bm25 \
  --generator llama \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K

# 4. Dense + GPT
echo "4/5: Dense + GPT"
python src/rag_system.py \
  --retriever dense \
  --generator gpt \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K

# 5. Dense + Llama
echo "5/5: Dense + Llama"
python src/rag_system.py \
  --retriever dense \
  --generator llama \
  --questions $QUESTIONS \
  --corpus $CORPUS \
  --top_k $TOP_K

echo "All configurations complete!"
```

Run with:
```bash
chmod +x run_all.sh
./run_all.sh
```

## Output Format

The output TSV files contain:
- **Column 1**: Generated answer
- **Column 2**: Metadata (JSON format) including:
  - Model name
  - Token usage
  - Retrieved document IDs (if using retrieval)
  - Retrieval scores (if using retrieval)
  - Any errors encountered

Example:
```
Denver Broncos	{"model": "gpt-4o-mini", "tokens_used": 125, "retrieved_doc_ids": ["0", "3"], "retrieval_scores": [0.95, 0.87]}
```

## System Components

### Retrievers

1. **BM25Retriever** (Open-weight, Sparse)
   - No API calls required
   - Fast, efficient sparse retrieval
   - Based on term frequency and inverse document frequency

2. **DenseRetriever** (API-based)
   - Uses OpenAI embeddings API
   - Semantic similarity search
   - Better for understanding context and meaning

### Generators

1. **GPTGenerator** (API-based)
   - Uses OpenAI GPT-4o-mini
   - High-quality answers
   - Requires API key and credits

2. **LlamaGenerator** (Open-weight)
   - Uses Meta's Llama models
   - Runs locally (GPU recommended)
   - No API costs

## Question Types Supported

The system handles multiple question types with appropriate formatting:

- **factoid**: Short, direct answers
- **list**: Numbered list responses
- **instruction**: Step-by-step numbered instructions
- **multiple choice**: Letter-only answers (A, B, C, D)

