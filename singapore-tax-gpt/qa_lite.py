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

print("🇸🇬 Singapore Tax Q&A System - Lite Version")
print("="*50)

from langchain_openai import ChatOpenAI

# Create LLM - Using Groq's Qwen for Chinese support
llm = ChatOpenAI(
    temperature=0,
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="qwen/qwen3-32b"
)

# Load structured tax facts
try:
    with open('singapore_tax_facts.json', 'r') as f:
        tax_facts = json.load(f)
        print("✅ Loaded tax facts")
except:
    tax_facts = {}
    print("⚠️ Tax facts not found")

print("✅ System ready!\n")

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
    
    # Create prompt based on language
    if is_chinese:
        prompt = f"""你是新加坡税务专家。请用中文回答。

用户问题：{question}

根据你对新加坡税务的了解，提供准确的答案。包括：
1. 直接回答问题
2. 提供具体的税率、金额或规则
3. 添加3-5个相关要点
4. 如果是2024年的最新信息，请说明

用中文详细回答："""
    else:
        prompt = f"""You are a Singapore tax expert. Answer in English.

User Question: {question}

Based on your knowledge of Singapore tax laws, provide an accurate answer including:
1. Direct answer to the question
2. Specific rates, amounts, or rules
3. 3-5 relevant bullet points
4. Note if information is for 2024

Answer in detail:"""
    
    # Get answer from LLM
    response = llm.invoke(prompt)
    
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