#!/usr/bin/env python
"""Lightweight Q&A system that doesn't build database on startup."""

import os
import json
import re
import warnings
from typing import Tuple
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment
load_dotenv()

# Disable telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from langchain_openai import ChatOpenAI

# Global LLM instance (initialized on first use)
llm = None

def get_llm():
    """Get or create the LLM instance."""
    global llm
    if llm is None:
        llm = ChatOpenAI(
            temperature=0,
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.environ.get("GROQ_API_KEY"),
            model_name="qwen/qwen3-32b"
        )
    return llm

# Load structured tax facts
try:
    with open('singapore_tax_facts.json', 'r') as f:
        tax_facts = json.load(f)
        pass  # Successfully loaded
except:
    tax_facts = {}
    pass  # No tax facts file

def split_multiple_questions(text):
    """Split text into individual questions."""
    questions = []
    
    # First check for multiple lines
    if '\n' in text:
        lines = text.strip().split('\n')
        for line in lines:
            clean = line.strip()
            if clean and len(clean) > 10:
                questions.append(clean)
    
    # If no multiple questions found, return original
    if not questions:
        questions = [text.strip()]
    
    return questions

def answer_single_question(question):
    """Answer using Groq directly without database."""
    
    # Detect language
    is_chinese = any(ord(char) > 0x4e00 and ord(char) < 0x9fff for char in question)
    
    # Create prompt based on language - CONCISE like GPT-4
    if is_chinese:
        prompt = f"""你是新加坡税务专家。简洁准确地回答，像ChatGPT一样自然对话。

{question}"""
    else:
        prompt = f"""You are a Singapore tax expert. Answer concisely like ChatGPT - be natural and direct. Keep responses under 50 words unless more detail is essential.

{question}"""
    
    # Get answer from LLM
    response = get_llm().invoke(prompt)
    
    # Clean up response
    answer = response.content
    
    # Remove thinking tags if present
    if "<think>" in answer:
        answer = answer.split("</think>")[-1].strip()
    
    # Clean markdown
    answer = answer.replace('**', '').replace('__', '')
    answer = re.sub(r'^#{1,6}\s+', '', answer, flags=re.MULTILINE)
    answer = answer.replace('###', '').replace('##', '').replace('#', '')
    
    return answer, ["Groq AI Knowledge Base"]

def answer_question(question):
    """Answer questions without database dependency."""
    
    # Check if there are multiple questions
    questions = split_multiple_questions(question)
    
    # If only one question, answer it directly
    if len(questions) == 1:
        return answer_single_question(questions[0])
    
    # Multiple questions - answer each
    all_answers = []
    all_sources = []
    
    for i, q in enumerate(questions, 1):
        answer, sources = answer_single_question(q)
        
        # Format with question number
        if len(questions) > 1:
            all_answers.append(f"Question {i}: {q}")
            all_answers.append("-" * 60)
        all_answers.append(answer)
        all_answers.append("")  # Empty line between questions
        
        all_sources.extend(sources)
    
    final_answer = "\n".join(all_answers).strip()
    unique_sources = list(set(all_sources))
    
    return final_answer, unique_sources

# For command line testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}\n")
        answer, sources = answer_question(question)
        print(f"Answer: {answer}\n")
    else:
        print("Ask any Singapore tax question:")
        while True:
            question = input("❓ Your question: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            answer, sources = answer_question(question)
            print(f"\n📝 Answer: {answer}\n")
            print("-"*50 + "\n")