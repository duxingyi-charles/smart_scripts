#!/usr/bin/env python3
"""
Academic Paper Text Cleaner

This script cleans text extracted from academic paper PDFs using GPT models. It handles common
issues in PDF-to-text conversion such as:
- Line numbers
- Page headers and footers
- Special characters and encoding issues
- Equation symbol corruption
- Paragraph structure preservation

The script processes large texts by:
1. Splitting the text into chunks based on token count
2. Attempting to split chunks at natural sentence boundaries
3. Using GPT to clean each chunk
4. Combining the cleaned chunks into a final output

Usage:
    python clean_academic_text.py input.txt output.txt [options]

Options:
    --model MODEL           GPT model to use (default: gpt-4o-mini)
    --max-chunk-tokens N    Maximum tokens per chunk (default: 10000)
    --debug-dir DIR        Directory to save debug chunks (if empty, debug output is disabled)

Requirements:
    - OpenAI API access (set OPENAI_API_KEY environment variable)
    - Python packages: openai, tiktoken

Example:
    python clean_academic_text.py paper.txt cleaned_paper.txt --model gpt-4o-mini --debug-dir debug_output
"""

import os
from openai import OpenAI
import tiktoken
from typing import List, Tuple
import argparse

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def split_text_by_tokens(text: str, max_tokens: int = 10000, model: str = "gpt-4o-mini") -> List[str]:
    """Split text into chunks based on token count, trying to split at natural sentence breaks."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    chunks = []
    sentence_breaks = [".", "!", "?", ";", ":"]
    current_pos = 0

    while current_pos < len(tokens):
        # Get the next chunk of tokens
        chunk_tokens = tokens[current_pos:current_pos + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        
        # If this is the last chunk or no sentence breaks found, use the entire chunk
        if current_pos + max_tokens >= len(tokens):
            chunks.append(chunk_text)
            break
        
        # Try to find the last sentence break
        last_break_pos = -1
        for break_token in sentence_breaks:
            pos = chunk_text.rfind(break_token)
            if pos > last_break_pos:
                last_break_pos = pos
        
        if last_break_pos != -1:
            # Split at the sentence break
            chunk_text = chunk_text[:last_break_pos + 1]
            # Calculate how many tokens we actually used
            used_tokens = len(encoding.encode(chunk_text))
            current_pos += used_tokens
        else:
            # If no sentence break found, use the whole chunk
            current_pos += len(chunk_tokens)
        
        chunks.append(chunk_text)
    
    return chunks

def read_file_in_chunks(file_path: str, max_tokens: int = 10000, model: str = "gpt-4o-mini") -> List[str]:
    """Read file and split into chunks based on token count."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return split_text_by_tokens(text, max_tokens, model)

def save_chunk_to_file(chunk: str, chunk_num: int, prefix: str, output_dir: str):
    """Save a chunk to a file for debugging."""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{prefix}_chunk_{chunk_num:03d}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(chunk)

def clean_text_with_gpt(text: str, model: str = "gpt-4o-mini") -> Tuple[str, int]:
    """Use GPT to clean academic text."""
    client = OpenAI()
    
    system_prompt = """You are a text cleaning assistant. Your task is to:
    1. Remove line numbers, page numbers, and headers/footers
    2. Remove special characters that are artifacts of PDF conversion
    3. Preserve the actual content including equations (convert corrupted equation symbols to proper ones if possible)
    4. Maintain the captions of figures and tables
    5. Maintain paragraph structure and section titles
    Return only the cleaned text without any explanations."""
    
    # Count tokens in the prompt and text
    text_tokens = count_tokens(text, model)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": f"Clean this academic text:\n\n{text}"}
            ],
            temperature=0.0,  # Keep it deterministic
            max_tokens=16000  # GPT-4o-mini max output tokens
        )
        return response.choices[0].message.content.strip(), text_tokens
    except Exception as e:
        print(f"Error in API call: {e}")
        return text, text_tokens  # Return original text if API call fails

def main():
    parser = argparse.ArgumentParser(description='Clean academic paper text using GPT')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('output_file', help='Path to save the cleaned output')
    parser.add_argument('--model', default='gpt-4o-mini', help='GPT model to use')
    parser.add_argument('--max-chunk-tokens', type=int, default=10000,
                      help='Maximum tokens per chunk (default: 10000 for GPT-4o-mini)')
    parser.add_argument('--debug-dir', default='',
                      help='Directory to save debug chunks (default: debug_chunks)')
    
    args = parser.parse_args()
    
    # Create debug directory
    if args.debug_dir:
        debug_dir = os.path.join(os.path.dirname(args.output_file), args.debug_dir)
        os.makedirs(debug_dir, exist_ok=True)
    else:
        debug_dir = ''
    
    # Read file in chunks based on token count
    chunks = read_file_in_chunks(args.input_file, args.max_chunk_tokens, args.model)
    
    # Process each chunk
    cleaned_chunks = []
    total_tokens_processed = 0
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{len(chunks)}...")
        
        # Save original chunk
        if debug_dir:
            save_chunk_to_file(chunk, i, "original", debug_dir)
        
        # Clean the chunk
        cleaned_chunk, chunk_tokens = clean_text_with_gpt(chunk, args.model)
        
        # Save cleaned chunk
        if debug_dir:
            save_chunk_to_file(cleaned_chunk, i, "cleaned", debug_dir)
        
        cleaned_chunks.append(cleaned_chunk)
        total_tokens_processed += chunk_tokens
        print(f"Processed {chunk_tokens} tokens in chunk {i}")
    
    # Write cleaned text to output file
    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_chunks))
    
    print(f"Cleaned text saved to {args.output_file}")
    print(f"Total tokens processed: {total_tokens_processed}")
    if debug_dir:
        print(f"Debug chunks saved in {debug_dir}")
        print(f"  - Original chunks: original_chunk_*.txt")
        print(f"  - Cleaned chunks: cleaned_chunk_*.txt")

if __name__ == "__main__":
    main()
