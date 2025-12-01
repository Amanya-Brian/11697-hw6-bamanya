#!/bin/bash
# evaluate_all.sh - Evaluate all prediction files

set -e

echo "========================================="
echo "Evaluating all RAG system predictions"
echo "========================================="
echo ""

# Configuration
QUESTIONS="data/question.tsv"
ANSWERS="data/answer.tsv"
PRED_DIR="output/prediction"
EVAL_DIR="output/evaluation"

# Create evaluation directory
mkdir -p $EVAL_DIR

echo "Configuration:"
echo "  Questions: $QUESTIONS"
echo "  Answers: $ANSWERS"
echo "  Predictions: $PRED_DIR"
echo "  Evaluation output: $EVAL_DIR"
echo ""

# Check if prediction files exist
if [ ! -d "$PRED_DIR" ]; then
    echo "Error: Prediction directory not found: $PRED_DIR"
    echo "Please run the RAG system first to generate predictions."
    exit 1
fi

# Count prediction files
NUM_PRED_FILES=$(find $PRED_DIR -name "*.tsv" 2>/dev/null | wc -l)
if [ $NUM_PRED_FILES -eq 0 ]; then
    echo "Error: No prediction files found in $PRED_DIR"
    echo "Please run the RAG system first."
    exit 1
fi

echo "Found $NUM_PRED_FILES prediction file(s) to evaluate"
echo ""

# Evaluate each prediction file
COUNTER=0
for pred_file in $PRED_DIR/*.tsv; do
    COUNTER=$((COUNTER + 1))
    
    filename=$(basename "$pred_file")
    echo "========================================="
    echo "[$COUNTER/$NUM_PRED_FILES] Evaluating: $filename"
    echo "========================================="
    
    # Run evaluation
    python src/evaluate.py \
        --prediction_file "$pred_file" \
        --questions $QUESTIONS \
        --answers $ANSWERS \
        --output "$EVAL_DIR/$filename"
    
    echo ""
done

echo "========================================="
echo "All evaluations complete!"
echo "========================================="
echo ""
echo "Evaluation results in $EVAL_DIR/:"
ls -lh $EVAL_DIR/
echo ""

# Generate summary report
echo "Generating summary report..."
python src/generate_summary.py \
    --eval_dir $EVAL_DIR \
    --output evaluation_summary.txt

echo ""
echo "Summary report saved to: evaluation_summary.txt"