import os
from pathlib import Path
from typing import List, Tuple, Dict
import re


def load_questions(questions_file: str) -> Tuple[List[str], List[str]]:
    """
    Load questions from TSV file
    
    Args:
        questions_file: Path to question.tsv file
        
    Returns:
        Tuple of (questions, question_types)
    """
    questions = []
    question_types = []
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                questions.append(parts[0].strip())
                question_types.append(parts[1].strip())
            else:
                questions.append(parts[0].strip() if parts else line)
                question_types.append('unknown')
    
    return questions, question_types


def load_answers(answers_file: str) -> List[List[str]]:
    """
    Load answers from TSV file
    
    Args:
        answers_file: Path to answer.tsv file
        
    Returns:
        List of answer lists (multiple answers per question)
    """
    answers = []
    
    with open(answers_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                answers.append([])
                continue
            
            answer_list = [a.strip() for a in line.split('\t') if a.strip()]
            answers.append(answer_list)
    
    return answers


def load_evidence(evidence_file: str) -> List[Dict[str, str]]:
    """
    Load evidence mapping from TSV file
    
    Args:
        evidence_file: Path to evidence.tsv file
        
    Returns:
        List of dicts with 'url' and 'filename' keys
    """
    evidence = []
    
    with open(evidence_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                evidence.append({'url': '', 'filename': ''})
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                evidence.append({
                    'url': parts[0].strip(),
                    'filename': parts[1].strip()
                })
            else:
                evidence.append({
                    'url': parts[0].strip() if parts else '',
                    'filename': ''
                })
    
    return evidence


def load_corpus(corpus_dir: str) -> List[Dict[str, str]]:
    """
    Load all documents from corpus directory
    
    Args:
        corpus_dir: Path to corpus directory
        
    Returns:
        List of document dicts with 'id', 'filename', 'content' keys
    """
    corpus_path = Path(corpus_dir)
    documents = []
    
    supported_extensions = ['.txt', '.md', '.pdf']
    
    for idx, filepath in enumerate(sorted(corpus_path.rglob('*'))):
        if filepath.is_file() and filepath.suffix.lower() in supported_extensions:
            try:
                content = load_document(filepath)
                
                documents.append({
                    'id': str(idx),
                    'filename': filepath.name,
                    'filepath': str(filepath),
                    'content': content
                })
            except Exception as e:
                print(f"Warning: Could not load {filepath}: {e}")
    
    return documents


def load_document(filepath: Path) -> str:
    """
    Load content from a single document file
    
    Args:
        filepath: Path to document file
        
    Returns:
        Document content as string
    """
    extension = filepath.suffix.lower()
    
    if extension in ['.txt', '.md']:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    elif extension == '.pdf':
        try:
            import PyPDF2
            content = []
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    content.append(page.extract_text())
            return '\n\n'.join(content)
        except ImportError:
            # Fallback: Try with pdfplumber if PyPDF2 fails
            try:
                import pdfplumber
                content = []
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            content.append(text)
                return '\n\n'.join(content)
            except ImportError:
                print(f"Warning: PDF libraries not available. Install PyPDF2 or pdfplumber.")
                return ""
    
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char in ['\n', '\t'])
    
    return text.strip()