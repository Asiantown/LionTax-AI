# Singapore Tax GPT 🇸🇬

AI-powered Singapore tax assistant with bilingual support (English/中文).

## Features
- **Bilingual Q&A**: Ask in English or Chinese, get answers in the same language
- **9 Tax Documents**: Searches through official IRAS tax acts
- **Fast Inference**: Powered by Groq (400 tokens/sec)
- **Smart Calculations**: Handles tax calculations for residents and non-residents

## Core Files
- `app_main.py` - Streamlit web interface
- `qa_working.py` - Q&A engine with document search
- `singapore_tax_facts.json` - Structured tax data
- `data/iras_docs/` - 9 PDF tax documents

## Setup
1. Get Groq API key from https://console.groq.com/
2. Add to `.env`: `GROQ_API_KEY=gsk_xxxxx`
3. Install: `pip install -r requirements.txt`
4. Run: `streamlit run app_main.py`

## Examples
- English: "What is the GST rate?"
- Chinese: "新加坡的个人所得税率是多少？"
- Calculation: "Calculate tax for $80,000"

## Tech Stack
- **LLM**: Groq Qwen3-32B (bilingual)
- **Framework**: LangChain + ChromaDB
- **UI**: Streamlit
- **Embeddings**: FakeEmbeddings (lightweight)